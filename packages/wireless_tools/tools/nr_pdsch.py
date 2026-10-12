"""NR PDSCH Tool — 5G NR PDSCH 端到端级联工具.

Chains together core physical layer tools for a complete PDSCH
transmission/reception chain (simplified, single code block, 1 layer):

TX: CRC24A → LDPC encode → rate match → symbol modulation → layer map → OFDM modulate
RX: OFDM demodulate → soft demodulation → layer demap → rate recovery → LDPC decode → CRC check

This is a convenience tool for Agent-based simulations — one command
runs the full chain instead of manually calling 6+ tools.
"""
from __future__ import annotations

import json
import sys
import os
import numpy as np

# Add tools directory to path for imports
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from nr_crc import _crc_encode_bits as crc_encode_bits, _crc_decode_bits as crc_decode_bits
from nr_ldpc import encode as ldpc_encode, decode as ldpc_decode
from nr_ldpc_rm import rate_match, rate_recover
from nr_modulation import modulate as sym_modulate, demodulate as sym_demodulate, soft_demodulate, bits_per_symbol
from nr_layer_map import layer_map, layer_demap
from nr_ofdm import ofdm_modulate, ofdm_demodulate

_BG_NSYS = {1: 22, 2: 10}
_BG_NCWNODES = {1: 66, 2: 50}


def pdsch_transmit(tb_bits: np.ndarray, bgn: int, modulation: str,
                   nfft: int, n_sc: int, n_symbols: int = 1,
                   rv: int = 0) -> dict:
    """Full PDSCH transmit chain.

    Args:
        tb_bits: Transport block bits (before CRC)
        bgn: LDPC base graph number (1 or 2)
        modulation: 'QPSK', '16QAM', '64QAM', '256QAM', '1024QAM'
        nfft: FFT size for OFDM
        n_sc: Number of active subcarriers
        n_symbols: Number of OFDM symbols
        rv: Redundancy version (0-3)

    Returns:
        dict with all intermediate results and final waveform
    """
    tb_bits = np.asarray(tb_bits, dtype=np.uint8).reshape(-1)
    nsys = _BG_NSYS[bgn]

    # Step 1: CRC24A attachment
    crc_bits = crc_encode_bits(tb_bits, '24A')  # includes TB + CRC
    n_info = len(crc_bits)
    zc = n_info // nsys
    if n_info != nsys * zc:
        raise ValueError(
            f"After CRC, info bits {n_info} not nsys({nsys})*Zc. "
            f"TB size {len(tb_bits)} may be wrong for BG{bgn}."
        )

    # Step 2: LDPC encode
    codeword = ldpc_encode(crc_bits.astype(np.int8), bgn)  # punctured output

    # Step 3: Rate match
    Qm = bits_per_symbol(modulation)
    outlen = n_sc * n_symbols * Qm  # total bits needed
    rm_bits = rate_match(codeword, outlen, rv, modulation, 1)

    # Step 4: Symbol modulation
    symbols = sym_modulate(rm_bits.astype(int), modulation)

    # Step 5: Layer mapping (1 layer)
    layered = layer_map(symbols, 1)  # (n_symbols_per_layer, 1)

    # Step 6: OFDM modulate
    # Reshape to (n_sc, n_symbols) grid
    grid = layered.reshape(n_sc, n_symbols)
    # Keep this simplified link model rectangular so its receiver can use the
    # conventional CP removal path without an OFDM windowing configuration.
    waveform = ofdm_modulate(grid, nfft, windowing=0)

    return {
        'tb_bits': tb_bits.tolist(),
        'tb_len': len(tb_bits),
        'crc_bits': crc_bits.tolist(),
        'n_info': n_info,
        'zc': zc,
        'ldpc_codeword': codeword.tolist(),
        'codeword_len': len(codeword),
        'rm_bits': rm_bits.tolist(),
        'rm_len': len(rm_bits),
        'outlen_target': outlen,
        'symbols_real': np.real(symbols).tolist(),
        'symbols_imag': np.imag(symbols).tolist(),
        'n_symbols': len(symbols),
        'layered_real': np.real(layered).flatten().tolist(),
        'layered_imag': np.imag(layered).flatten().tolist(),
        'waveform_real': np.real(waveform).tolist(),
        'waveform_imag': np.imag(waveform).tolist(),
        'waveform_len': len(waveform),
    }


def pdsch_receive(waveform: np.ndarray, bgn: int, modulation: str,
                  nfft: int, n_sc: int, n_symbols: int = 1,
                  rv: int = 0, max_iter: int = 8,
                  noise_var: float = 1.0, zc: int | None = None) -> dict:
    """Full PDSCH receive chain.

    Args:
        waveform: Received OFDM waveform samples
        bgn: LDPC base graph number (1 or 2)
        modulation: 'QPSK', '16QAM', '64QAM', '256QAM', '1024QAM'
        nfft: FFT size for OFDM
        n_sc: Number of active subcarriers
        n_symbols: Number of OFDM symbols
        rv: Redundancy version (0-3)
        max_iter: Max LDPC decoding iterations
        noise_var: Noise variance for soft demodulation
        zc: LDPC lifting size. If None, estimated from rm_len (may fail
            with heavy puncturing). Providing zc explicitly is recommended.

    Returns:
        dict with decoded transport block and intermediate results
    """
    waveform = np.asarray(waveform, dtype=np.complex128).reshape(-1)
    nsys = _BG_NSYS[bgn]
    ncw = _BG_NCWNODES[bgn]
    Qm = bits_per_symbol(modulation)

    # Step 1: OFDM demodulate
    grid = ofdm_demodulate(waveform, n_sc, nfft, n_symbols, windowing=0)  # (n_sc, n_symbols)

    # Step 2: Layer demapping (1 layer = reshape)
    symbols = grid.reshape(-1)  # flatten to 1D symbol vector

    # Step 3: Soft demodulation (LLR)
    llr_sym = soft_demodulate(symbols, modulation, noise_var)

    # Step 4: Rate recovery
    rm_len = n_sc * n_symbols * Qm
    if zc is None:
        # Estimate zc — works best when rm_len is close to codeword length
        # (low puncturing). With heavy puncturing, provide zc explicitly.
        punctured_nodes = ncw - 2
        zc = max(1, rm_len // punctured_nodes)
        # Adjust upward until info bits fit CRC
        while nsys * zc < 24:
            zc += 1

    codeword_len = ncw * zc
    llr_cw = rate_recover(llr_sym, codeword_len, rv, modulation, 1, bgn)

    # Step 5: LDPC decode
    info_bits = ldpc_decode(llr_cw, bgn, max_iter)

    # Step 6: CRC check and decode
    tb_bits, crc_error = crc_decode_bits(info_bits.astype(np.uint8), '24A')

    return {
        'grid_real': np.real(grid).tolist(),
        'grid_imag': np.imag(grid).tolist(),
        'symbols_real': np.real(symbols).tolist(),
        'symbols_imag': np.imag(symbols).tolist(),
        'llr': llr_sym.tolist(),
        'llr_cw': llr_cw.tolist(),
        'decoded_info': info_bits.tolist(),
        'tb_bits': tb_bits.tolist(),
        'tb_len': len(tb_bits),
        'crc_ok': not crc_error,
        'zc_estimate': zc,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NR PDSCH end-to-end tool")
    parser.add_argument('--mode', choices=['tx', 'rx'], required=True,
                        help="tx=transmit chain, rx=receive chain")
    parser.add_argument('--bgn', type=int, choices=[1, 2], required=True,
                        help="LDPC base graph number")
    parser.add_argument('--modulation', choices=['QPSK', '16QAM', '64QAM', '256QAM', '1024QAM'],
                        required=True, help="modulation scheme")
    parser.add_argument('--nfft', type=int, default=128, help="FFT size")
    parser.add_argument('--n-sc', type=int, default=12, help="number of active subcarriers")
    parser.add_argument('--n-symbols', type=int, default=1, help="number of OFDM symbols")
    parser.add_argument('--rv', type=int, default=0, help="redundancy version (0-3)")
    parser.add_argument('--tb-bits', help="TX: comma-separated transport block bits")
    parser.add_argument('--waveform', help='RX: JSON array of complex waveform (real, imag pairs as flat list)')
    parser.add_argument('--noise-var', type=float, default=1.0, help="RX: noise variance for soft demod")
    parser.add_argument('--max-iter', type=int, default=8, help="RX: max LDPC iterations")
    parser.add_argument('--zc', type=int, default=None, help="RX: LDPC lifting size (recommended)")
    args = parser.parse_args()

    if args.mode == 'tx':
        tb = np.array([int(b) for b in args.tb_bits.split(',')], dtype=np.uint8)
        result = pdsch_transmit(tb, args.bgn, args.modulation,
                                args.nfft, args.n_sc, args.n_symbols, args.rv)
        result['mode'] = 'tx'
        result['bgn'] = args.bgn
        result['modulation'] = args.modulation
        result['nfft'] = args.nfft
        result['n_sc'] = args.n_sc
        result['n_symbols'] = args.n_symbols
        result['rv'] = args.rv
        print(json.dumps(result))
    else:
        # Waveform as flat list of [re1, im1, re2, im2, ...]
        wf_flat = json.loads(args.waveform)
        wf_complex = np.array(wf_flat[0::2]) + 1j * np.array(wf_flat[1::2])
        result = pdsch_receive(wf_complex, args.bgn, args.modulation,
                               args.nfft, args.n_sc, args.n_symbols,
                               args.rv, args.max_iter, args.noise_var, args.zc)
        result['mode'] = 'rx'
        result['bgn'] = args.bgn
        result['modulation'] = args.modulation
        print(json.dumps(result))


if __name__ == '__main__':
    main()
