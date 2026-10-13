"""nr_pusch - 5G NR Physical Uplink Shared Channel (PUSCH) 编码/解码。

Implements TS 38.211 Sections 6.3.1.1 - 6.3.1.5 PUSCH processing.
MATLAB equivalent: nrPUSCH(...) and nrPUSCHDecode(...)

简化版语法（无配置对象）：

编码方向：
  sym = nrPUSCH(cw, modulation, nlayers, ncellid, rnti)
  sym = nrPUSCH(cw, modulation, nlayers, ncellid, rnti, tprecode, mrb)

解码方向：
  [cw, symbols] = nrPUSCHDecode(sym, modulation, nid, rnti)
  [cw, symbols] = nrPUSCHDecode(sym, modulation, nid, rnti, nvar, tprecode, mrb)

处理链：
  编码: 加扰 -> 调制 -> 层映射 -> [变换预编码(DFT-s-OFDM)]
  解码: [变换解预编码] -> 层解映射 -> 软解调 -> 解扰
"""
from __future__ import annotations

import argparse
import json
import sys
import os

import numpy as np

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nr_prbs import prbs
from nr_modulation import modulate, soft_demodulate
from nr_layer_map import layer_map, layer_demap


def pusch_prbs(nid: int, rnti: int, n: int, q: int = 0, mapping: str = "binary") -> np.ndarray:
    """Generate PUSCH scrambling sequence per TS 38.211 Section 6.3.1.1.

    Args:
        nid: PUSCH scrambling identity (0..1023)
        rnti: Radio network temporary identifier (0..65535)
        n: Length of the sequence
        q: Codeword number (0 or 1), default 0
        mapping: 'binary' (0/1) or 'signed' (1/-1)

    Returns:
        PUSCH scrambling sequence of length n
    """
    if nid < 0 or nid > 1023:
        raise ValueError(f"nid must be 0..1023, got {nid}")
    if rnti < 0 or rnti > 65535:
        raise ValueError(f"rnti must be 0..65535, got {rnti}")

    # c_init = rnti * 2^15 + nid
    cinit = rnti * (2 ** 15) + nid

    # Generate PRBS using the same Gold sequence as nrPRBS
    # For second codeword (q=1), advance the sequence by 2^31 samples
    if q == 1:
        # Skip first 2^31 samples for second codeword
        skip = 2 ** 31
        seq = prbs(cinit, [skip, n], mapping="binary")
    else:
        seq = prbs(cinit, n, mapping="binary")

    if mapping == "signed":
        return np.where(seq == 0, 1, -1).astype(float)
    return seq.astype(int)


def pusch_scramble(cw: np.ndarray, nid: int, rnti: int) -> np.ndarray:
    """PUSCH scrambling: XOR codeword bits with PRBS.

    Args:
        cw: Codeword bits (0/1), 1-D array
        nid: Scrambling identity (0..1023)
        rnti: RNTI (0..65535)

    Returns:
        Scrambled bits (0/1)
    """
    cw = np.asarray(cw, dtype=np.int8).reshape(-1)
    c = pusch_prbs(nid, rnti, len(cw), q=0, mapping="binary")
    return np.bitwise_xor(cw, c)


def pusch_descramble(soft_bits: np.ndarray, nid: int, rnti: int) -> np.ndarray:
    """PUSCH descrambling: soft XOR with PRBS.

    Args:
        soft_bits: Soft bit LLR values, 1-D array
        nid: Scrambling identity (0..1023)
        rnti: RNTI (0..65535)

    Returns:
        Descrambled soft bits
    """
    soft_bits = np.asarray(soft_bits, dtype=float).reshape(-1)
    c = pusch_prbs(nid, rnti, len(soft_bits), q=0, mapping="binary")
    # Soft descramble: multiply by (-1)^c
    signs = 1 - 2 * c  # 0 -> +1, 1 -> -1
    return soft_bits * signs


def transform_precode(symbols: np.ndarray, mrb: int) -> np.ndarray:
    """DFT-s-OFDM transform precoding.

    Args:
        symbols: Modulated symbols, 1-D array
        mrb: Number of resource blocks allocated

    Returns:
        DFT-precoded symbols
    """
    n_symbols = len(symbols)
    return np.fft.fft(symbols) / np.sqrt(n_symbols)


def transform_deprecode(symbols: np.ndarray, mrb: int) -> np.ndarray:
    """DFT-s-OFDM transform deprecoding (IDFT).

    Args:
        symbols: DFT-precoded symbols, 1-D array
        mrb: Number of resource blocks allocated

    Returns:
        Original modulated symbols
    """
    n_symbols = len(symbols)
    return np.fft.ifft(symbols) * np.sqrt(n_symbols)


def pusch_encode(cw: np.ndarray, modulation: str, nlayers: int,
                 ncellid: int, rnti: int, tprecode: bool = False,
                 mrb: int = 1) -> np.ndarray:
    """PUSCH encoding: scramble -> modulate -> layer map -> [transform precode].

    Args:
        cw: Codeword bits (0/1), 1-D array
        modulation: Modulation scheme ('pi/2-BPSK', 'QPSK', '16QAM', '64QAM', '256QAM')
        nlayers: Number of layers (1..4)
        ncellid: Physical cell identity (0..1007), used as scrambling identity
        rnti: RNTI (0..65535)
        tprecode: Enable transform precoding (DFT-s-OFDM), default False
        mrb: Number of resource blocks for transform precoding, default 1

    Returns:
        PUSCH symbols, shape [n_symbols, nlayers]
    """
    cw = np.asarray(cw, dtype=np.int8).reshape(-1)

    # Step 1: Scrambling
    scrambled = pusch_scramble(cw, ncellid, rnti)

    # Step 2: Modulation
    mod_symbols = modulate(scrambled, modulation)

    # Step 3: Layer mapping
    layered = layer_map(mod_symbols, nlayers)

    # Step 4: Transform precoding (optional)
    if tprecode:
        # Apply DFT-s-OFDM per layer
        for l in range(nlayers):
            layered[:, l] = transform_precode(layered[:, l], mrb)

    return layered


def pusch_decode(sym: np.ndarray, modulation: str, nid: int, rnti: int,
                 nvar: float = 1e-10, tprecode: bool = False,
                 mrb: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """PUSCH decoding: [transform deprecode] -> layer demap -> soft demodulate -> descramble.

    Args:
        sym: Received PUSCH symbols, shape [n_symbols, nlayers]
        modulation: Modulation scheme
        nid: Scrambling identity (0..1023)
        rnti: RNTI (0..65535)
        nvar: Noise variance for soft demodulation, default 1e-10
        tprecode: Enable transform deprecoding, default False
        mrb: Number of resource blocks for transform deprecoding, default 1

    Returns:
        soft_bits: Descrambled soft bit LLR values
        demapped: Layer-demapped received symbols
    """
    sym = np.asarray(sym, dtype=complex)
    if sym.ndim == 1:
        sym = sym[:, None]

    # Step 1: Transform deprecoding (optional)
    if tprecode:
        nlayers = sym.shape[1]
        for l in range(nlayers):
            sym[:, l] = transform_deprecode(sym[:, l], mrb)

    # Step 2: Layer demapping
    nlayers = sym.shape[1]
    demapped = layer_demap(sym, nlayers)

    # Step 3: Soft demodulation
    soft_bits = soft_demodulate(demapped, modulation, nvar)

    # Step 4: Descrambling
    descrambled = pusch_descramble(soft_bits, nid, rnti)

    return descrambled, demapped


def parse_complex(text: str) -> np.ndarray:
    """Parse complex JSON array."""
    value = json.loads(text)
    if isinstance(value, dict):
        real = np.asarray(value.get("real", []), dtype=float)
        imag = np.asarray(value.get("imag", np.zeros_like(real)), dtype=float)
        if real.shape != imag.shape:
            raise ValueError("real and imag arrays must have the same shape")
        return real + 1j * imag
    return np.asarray(value, dtype=complex)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NR PUSCH — 5G NR Physical Uplink Shared Channel 编码/解码",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  # 编码
  python tools/nr_pusch.py --mode encode --bits 0,1,1,0,1,0,0,1 --modulation QPSK \\
      --nlayers 1 --ncellid 17 --rnti 111

  # 解码
  python tools/nr_pusch.py --mode decode --symbols '{"real":[...],"imag":[...]}' \\
      --modulation QPSK --nid 17 --rnti 111

  # 带变换预编码的编码
  python tools/nr_pusch.py --mode encode --bits 0,1,1,0,1,0,0,1 --modulation QPSK \\
      --nlayers 1 --ncellid 17 --rnti 111 --tprecode --mrb 1
""",
    )

    parser.add_argument("--mode", choices=["encode", "decode"], required=True,
                        help="操作模式：encode（编码）或 decode（解码）")

    # 编码输入
    parser.add_argument("--bits", default=None,
                        help="[编码] 逗号分隔的比特串，如 0,1,1,0")

    # 解码输入
    parser.add_argument("--symbols", default=None,
                        help='[解码] 接收符号 JSON，格式：{"real":[...],"imag":[...]}')

    # 公共参数
    parser.add_argument("--modulation", default="QPSK",
                        choices=["pi/2-BPSK", "QPSK", "16QAM", "64QAM", "256QAM"],
                        help="调制方式（默认 QPSK）")
    parser.add_argument("--nlayers", type=int, default=1,
                        help="[编码] 层数（1..4），默认 1")
    parser.add_argument("--ncellid", type=int, default=None,
                        help="[编码] 物理小区 ID（0..1007），用作加扰身份")
    parser.add_argument("--nid", type=int, default=None,
                        help="[解码] 加扰身份（0..1023）")
    parser.add_argument("--rnti", type=int, default=None,
                        help="RNTI（0..65535）")

    # 变换预编码
    parser.add_argument("--tprecode", action="store_true",
                        help="启用变换预编码（DFT-s-OFDM）")
    parser.add_argument("--mrb", type=int, default=1,
                        help="资源块数量（用于变换预编码），默认 1")

    # 解码参数
    parser.add_argument("--nvar", type=float, default=1e-10,
                        help="[解码] 噪声方差（默认 1e-10）")

    args = parser.parse_args()

    try:
        if args.mode == "encode":
            if args.bits is None or args.ncellid is None or args.rnti is None:
                raise ValueError("编码模式需要 --bits、--ncellid、--rnti")
            cw = np.array([int(b) for b in args.bits.split(",")], dtype=np.int8)
            sym = pusch_encode(cw, args.modulation, args.nlayers,
                               args.ncellid, args.rnti, args.tprecode, args.mrb)
            result = {
                "symbols_real": sym.real.tolist(),
                "symbols_imag": sym.imag.tolist(),
                "n_symbols": sym.shape[0],
                "n_layers": sym.shape[1],
            }
        else:  # decode
            if args.symbols is None or args.nid is None or args.rnti is None:
                raise ValueError("解码模式需要 --symbols、--nid、--rnti")
            sym = parse_complex(args.symbols)
            soft_bits, demapped = pusch_decode(
                sym, args.modulation, args.nid, args.rnti,
                args.nvar, args.tprecode, args.mrb
            )
            result = {
                "soft_bits": soft_bits.tolist(),
                "n_bits": len(soft_bits),
            }

        print(json.dumps(result))

    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
