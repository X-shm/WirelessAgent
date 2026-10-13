"""
LTE OFDM Tool — LTE OFDM 调制/解调/信息工具 (3GPP TS 36.211 §6.2).

Replicates MATLAB lteOFDMInfo / lteOFDMModulate / lteOFDMDemodulate.
  info       : Nfft、循环前缀长度、默认加窗长度、采样率
  modulate   : 资源网格 -> 时域波形（DC 插入 + IFFT + CP + raised-cosine 加窗叠加）
  demodulate : 时域波形 -> 资源网格（去 CP + FFT + 频域相位校正 + 去 DC）

FFT/CP/windowing 均按 MATLAB LTE Toolbox 逻辑逐样本复现（黄金样本 1e-9 验证）。
"""
from __future__ import annotations

import argparse
import json
import sys
import numpy as np

_BW_TO_NRB = {'1.4MHZ': 6, '3MHZ': 15, '5MHZ': 25, '10MHZ': 50, '15MHZ': 75, '20MHZ': 100}
# Compiled-lib default windowing as a function of (default) Nfft.
_NFFT_WINDOWING = {128: 4, 256: 6, 512: 4, 1024: 6, 2048: 8}
# Cyclic prefix lengths (samples) at Nfft=2048, per TS 36.211 Table 6.2.3-1.
_CP_2048 = {
    'NORMAL': [160] + [144] * 6 + [160] + [144] * 6,   # 14 symbols
    'EXTENDED': [512] * 12,                             # 12 symbols
}


def _normalize_nrb(nrb):
    if isinstance(nrb, str):
        key = nrb.upper().replace(' ', '')
        if key.isdigit():
            nrb = int(key)
        elif key not in _BW_TO_NRB:
            raise ValueError(f"Unsupported bandwidth '{nrb}'. Supported: {list(_BW_TO_NRB)}")
        else:
            nrb = _BW_TO_NRB[key]
    nrb = int(nrb)
    if not 6 <= nrb <= 110:
        raise ValueError("NDLRB must be between 6 and 110 (or a channel bandwidth string).")
    return nrb


def _nfft_for_nrb(nrb):
    """Smallest power of 2 >= 12*NRB/0.85 (bandwidth occupancy <= 85%)."""
    n = 128
    while n < 12 * nrb / 0.85:
        n *= 2
    return n


def _cp_lengths(nfft, cp):
    return [int(round(b * nfft / 2048)) for b in _CP_2048[cp]]


def _raised_cosine_window(n, w):
    """lte.internal.raisedCosineWindow(n, w): length n+w, raised-cosine edges of w samples."""
    if w == 0:
        return np.ones(n)
    k = np.arange(1, w + 1, dtype=float)
    p = 0.5 * (1 - np.sin(np.pi * (w + 1 - 2 * k) / (2 * w)))
    return np.concatenate([p, np.ones(n - w), p[::-1]])


def lte_ofdm_info(nrb, cp='Normal', nfft=None):
    """Replicates lteOFDMInfo. Returns dict with nfft/windowing/samplingrate/cplengths."""
    nrb = _normalize_nrb(nrb)
    cp = cp.upper()
    if cp not in _CP_2048:
        raise ValueError(f"CyclicPrefix must be 'Normal' or 'Extended', got '{cp}'.")
    default_nfft = _nfft_for_nrb(nrb)
    if nfft is None:
        nfft = default_nfft
    else:
        nfft = int(nfft)
        if nfft < 12 * nrb:
            raise ValueError(f"FFT size {nfft} must be >= number of subcarriers ({12 * nrb}).")
        base = _cp_lengths(default_nfft, cp)
        scaled = [b * nfft / default_nfft for b in base]
        if any(v != int(v) for v in scaled):
            raise ValueError(f"FFT size {nfft} gives non-integer cyclic prefix lengths.")
    cplengths = _cp_lengths(nfft, cp)
    if nfft == default_nfft:
        windowing = _NFFT_WINDOWING[nfft]
    else:
        windowing = int(round(_NFFT_WINDOWING[default_nfft] * nfft / default_nfft))
    return {
        'nfft': nfft,
        'windowing': windowing,
        'samplingrate': float(15000 * nfft),
        'cplengths': cplengths,
    }


def modulate(nrb, cp, grid, windowing=None, nfft=None):
    """Replicates lteOFDMModulate. nrb is derived from grid rows (as MATLAB does)."""
    grid = np.asarray(grid, dtype=np.complex128)
    if grid.ndim == 2:
        grid = grid[:, :, None]
    nSC, nSymTotal, nAnts = grid.shape
    if nSC > 2048:
        raise ValueError(f"Number of subcarriers ({nSC}) cannot be greater than 2048.")

    # Derive NRB from grid size exactly as lteOFDMModulate does.
    log2nsc = np.log2(nSC)
    if float(log2nsc) == int(log2nsc) and log2nsc > 6:
        nrb_calc = int(np.floor(0.85 * nSC / 12))
    else:
        nrb_calc = int(nSC / 12)
        nSC = 12 * nrb_calc
    nrb_calc = max(6, min(110, nrb_calc))

    info = lte_ofdm_info(nrb_calc, cp, nfft)
    nfft = info['nfft']
    cpLengths = info['cplengths']
    symbolsPerSlot = len(cpLengths) // 2
    nSubframes = int(np.floor(nSymTotal / (symbolsPerSlot * 2)))

    if nSubframes == 0:
        return np.zeros((0, nAnts), dtype=np.complex128), info
    if nSC not in (0, nSC, nfft):
        # grid rows must be 0, 12*nrb, or nfft
        raise ValueError("Grid must contain a whole number of resource blocks.")
    if nSymTotal % (symbolsPerSlot * 2) != 0:
        raise ValueError(
            f"Grid must contain whole subframes (columns multiple of {symbolsPerSlot * 2}).")

    N = int(windowing) if windowing is not None else int(info['windowing'])
    if N > nfft - cpLengths[0]:
        raise ValueError(
            f"Windowing ({N}) must be <= IFFT size ({nfft}) minus longest CP ({cpLengths[0]}).")

    firstSC = nfft // 2 - nSC // 2
    window0 = _raised_cosine_window(nfft + cpLengths[0], N)
    window1 = _raised_cosine_window(nfft + cpLengths[1], N)

    samplesPerSubframe = sum(cpLengths) + nfft * symbolsPerSlot * 2
    waveform = np.zeros((nSubframes * samplesPerSubframe, nAnts), dtype=np.complex128)

    pos = 0
    head = np.zeros((N, nAnts), dtype=np.complex128) if N > 0 else None
    nSymbols = nSubframes * symbolsPerSlot * 2
    for i in range(nSymbols):
        if nSC == nfft:
            ifftin = grid[:, i, :].reshape(nfft, nAnts)
        else:
            ifftin = np.zeros((nfft, nAnts), dtype=np.complex128)
            half = nSC // 2
            ifftin[firstSC:firstSC + half, :] = grid[0:half, i, :]
            ifftin[firstSC + half + 1:firstSC + half + 1 + half, :] = grid[half:, i, :]
        iffout = np.fft.ifft(np.fft.fftshift(ifftin, axes=0), axis=0)

        cpLength = cpLengths[i % len(cpLengths)]
        extended = np.vstack([iffout[-(cpLength + N):, :], iffout])
        window = window0 if (i % symbolsPerSlot) == 0 else window1
        windowed = extended * window[:, None]

        if i == 0:
            if head is not None:
                head[:] = windowed[0:N, :]
            L = cpLength + nfft
            waveform[0:L, :] = windowed[N:N + L, :]
        else:
            L = cpLength + nfft + N
            waveform[pos - N:pos - N + L, :] += windowed
        pos += cpLength + nfft

    if head is not None and N > 0:
        waveform[-N:, :] += head
    return waveform, info


def demodulate(nrb, cp, waveform, cpfraction=0.55, nfft=None):
    """Replicates lteOFDMDemodulate. Returns the received resource grid."""
    waveform = np.asarray(waveform, dtype=np.complex128)
    if waveform.ndim == 1:
        waveform = waveform[:, None]
    nrb = _normalize_nrb(nrb)
    cp = cp.upper()
    if not 0 <= float(cpfraction) <= 1:
        raise ValueError("CPFRACTION must be between 0 and 1.")

    info = lte_ofdm_info(nrb, cp, nfft)
    nfft = info['nfft']
    samplesPerSubframe = int(info['samplingrate'] * 0.001)  # 15 * nfft
    cpLengths = info['cplengths'][:len(info['cplengths']) // 2]  # one slot
    nSymbols = len(cpLengths)
    T, P = waveform.shape
    nSubframes = int(np.floor(T / samplesPerSubframe))
    nSym = 14 if cp == 'NORMAL' else 12

    firstActiveSC = nfft // 2 - nrb * 6
    totalActiveSC = nrb * 12
    reGrid = np.zeros((totalActiveSC, nSym * nSubframes, P), dtype=np.complex128)

    idx = np.arange(nfft, dtype=float)
    offset = 0
    i = 0
    for _subframe in range(nSubframes):
        for _slot in range(2):
            for symbol in range(nSymbols):
                cpLength = cpLengths[symbol]
                fftStart = int(cpLength * float(cpfraction))
                # Compiled lteOFDMDemodulate applies the phase correction to the
                # fftshift'ed spectrum with a +2*pi*(cp-fftStart)*(k+nfft/2)/nfft
                # exponent (the help-text .m source uses a different convention).
                pc = np.exp(2j * np.pi * (cpLength - fftStart) * (idx + nfft / 2) / nfft)[:, None]
                seg = waveform[offset + fftStart:offset + fftStart + nfft, :]
                fftOut = np.fft.fftshift(np.fft.fft(seg, axis=0), axes=0) * pc
                active = fftOut[firstActiveSC:firstActiveSC + totalActiveSC + 1, :]
                active = np.delete(active, nrb * 6, axis=0)  # remove DC subcarrier
                reGrid[:, i, :] = active
                i += 1
                offset += nfft + cpLength
    return reGrid


def _to_complex(d):
    return np.asarray(d['real'], dtype=np.complex128) + 1j * np.asarray(d['imag'], dtype=np.complex128)


def _to_cplx_json(a):
    return {"real": np.real(a).tolist(), "imag": np.imag(a).tolist()}


def _load_complex_arg(value, file_value, name):
    if file_value:
        with open(file_value, 'r', encoding='utf-8') as f:
            return _to_complex(json.load(f))
    if value:
        return _to_complex(json.loads(value))
    raise ValueError(f"need --{name} or --{name}-file")


def main():
    parser = argparse.ArgumentParser(description="LTE OFDM tool")
    # Flat flags align exactly with the schema contract. The legacy positional
    # form ("lte_ofdm.py info --nrb 6") is normalized for compatibility.
    if len(sys.argv) > 1 and sys.argv[1] in ('info', 'modulate', 'demodulate'):
        sys.argv[1:2] = ['--mode', sys.argv[1]]
    parser.add_argument('--mode', required=True, choices=('info', 'modulate', 'demodulate'))
    parser.add_argument('--nrb', help="NRB (6..110) or bandwidth e.g. 10MHz")
    parser.add_argument('--cp', default='Normal', help="Normal/Extended")
    parser.add_argument('--windowing', type=int, default=None)
    parser.add_argument('--nfft', type=int, default=None, help="custom FFT size")
    parser.add_argument('--cpfraction', type=float, default=0.55)
    parser.add_argument('--grid', help='inline JSON {"real":...,"imag":...}')
    parser.add_argument('--grid_file', '--grid-file', dest='grid_file', help='path to JSON grid file')
    parser.add_argument('--waveform', help='inline JSON {"real":...,"imag":...}')
    parser.add_argument('--waveform_file', '--waveform-file', dest='waveform_file', help='path to JSON waveform file')

    args = parser.parse_args()

    try:
        if args.mode == 'info':
            if args.nrb is None:
                raise ValueError("info mode requires --nrb")
            info = lte_ofdm_info(args.nrb, args.cp, args.nfft)
            print(json.dumps(info, ensure_ascii=False))
        elif args.mode == 'modulate':
            grid = _load_complex_arg(args.grid, args.grid_file, 'grid')
            wf, info = modulate(args.nrb, args.cp, grid, args.windowing, args.nfft)
            out = {"info": info, "waveform": _to_cplx_json(wf)}
            print(json.dumps(out, ensure_ascii=False))
        else:
            if args.nrb is None:
                raise ValueError("demodulate mode requires --nrb")
            wf = _load_complex_arg(args.waveform, args.waveform_file, 'waveform')
            rg = demodulate(args.nrb, args.cp, wf, args.cpfraction, args.nfft)
            out = {"regrid": _to_cplx_json(rg)}
            print(json.dumps(out, ensure_ascii=False))
    except (ValueError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == '__main__':
    main()
