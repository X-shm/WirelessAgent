"""NR Timing Estimate — 5G NR 接收机定时估计。

对应 MATLAB 5G Toolbox 的 nrTimingEstimate。

两种调用模式：
  1. 直接模式（简化）：提供 --waveform 和 --ref_waveform，直接互相关
  2. 完整模式（推荐）：提供 --waveform、--ref_ind、--ref_sym、--nrb、--scs、--nslot，
     工具内部自动构造参考资源网格并用 OFDM 调制生成参考波形，然后互相关

核心逻辑：
  1. 构造参考波形（直接输入 or 内部生成）
  2. 对每个接收天线与参考端口组合计算互相关
  3. 取正延迟段（delay = 0 .. T_eff-1）
  4. 跨端口、跨天线累加相关幅度
  5. 可选：应用门限和最大延迟窗口
  6. 峰值位置即为定时偏移（0-based）
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import parse_complex, complex_json


def _build_reference_waveform(ref_ind, ref_sym, nrb, scs, nslot, nsym=14):
    """从参考索引和符号构造参考波形。

    Parameters
    ----------
    ref_ind : array_like, 1-D
        参考信号的线性索引（0-based），地址为 (nsc*nsym,) 展平后的资源网格。
    ref_sym : array_like, 1-D or 2-D
        参考符号。1-D 时为单端口；2-D 形状 [n_ind, P] 时为多端口。
    nrb : int
        资源块数量。
    scs : float
        子载波间隔（kHz）。
    nslot : int
        初始时隙号（0-based）。
    nsym : int, optional
        每时隙 OFDM 符号数，默认 14。

    Returns
    -------
    ref_waveform : ndarray, shape [T_ref, P]
        参考波形，P 个端口。
    """
    from nr_ofdm import ofdm_modulate

    nsc = nrb * 12
    n_ports = 1

    # 处理 ref_sym 维度
    ref_sym = np.asarray(ref_sym, dtype=complex)
    if ref_sym.ndim == 2:
        n_ports = ref_sym.shape[1]

    # 构造资源网格 [nsc, nsym, n_ports]
    ref_grid = np.zeros((nsc, nsym, n_ports), dtype=complex)

    ref_ind_arr = np.asarray(ref_ind, dtype=int)

    if ref_sym.ndim == 1:
        # 单端口：ref_ind 直接索引到 2D 网格
        for i, idx in enumerate(ref_ind_arr):
            if idx < 0 or idx >= nsc * nsym:
                continue
            row = idx % nsc  # subcarrier
            col = idx // nsc  # symbol
            if col < nsym:
                ref_grid[row, col, 0] = ref_sym[i] if i < len(ref_sym) else 0
    else:
        # 多端口：ref_ind 是 2D 索引，ref_sym 形状 [n_ind, n_ports]
        for i, idx in enumerate(ref_ind_arr):
            if idx < 0 or idx >= nsc * nsym:
                continue
            row = idx % nsc
            col = idx // nsc
            if col < nsym and i < ref_sym.shape[0]:
                ref_grid[row, col, :] = ref_sym[i, :]

    # OFDM 调制每个端口，拼接成 [T_ref, n_ports]
    # nfft 根据 nrb 选择：最小满足 >= nsc 的 2 的幂
    nfft = 1
    while nfft < nsc:
        nfft *= 2
    nfft = max(nfft, 128)  # 最小 128 点

    port_waveforms = []
    for p in range(n_ports):
        grid_2d = ref_grid[:, :, p]  # [nsc, nsym]
        wave = ofdm_modulate(grid_2d, nfft, scs)
        port_waveforms.append(wave)

    # 确保所有端口长度一致（取最小长度）
    min_len = min(len(w) for w in port_waveforms)
    ref_waveform = np.zeros((min_len, n_ports), dtype=complex)
    for p in range(n_ports):
        ref_waveform[:, p] = port_waveforms[p][:min_len]

    return ref_waveform


def nr_timing_estimate(waveform, ref_waveform, threshold=0.0, max_delay=None):
    """基于互相关的 NR 定时估计。

    Parameters
    ----------
    waveform : array_like, shape (T, R) or (T,)
        接收复波形，T 个采样点，R 个接收天线。
    ref_waveform : array_like, shape (T_ref, P) or (T_ref,)
        参考复波形，T_ref 个采样点，P 个参考端口。
    threshold : float, optional
        相关幅度门限（0..1），低于此值返回 None。默认 0（不检测）。
    max_delay : int, optional
        最大延迟搜索范围（样本数），默认搜索全部。

    Returns
    -------
    offset : int or None
        估计的定时偏移（样本数，0-based），若低于门限返回 None。
    mag : list of float
        跨天线+端口求和后的相关幅度曲线。
    peak_magnitude : float
        峰值幅度值。
    """
    wave = np.asarray(waveform, dtype=complex)
    ref = np.asarray(ref_waveform, dtype=complex)

    if wave.ndim == 1:
        wave = wave[:, None]
    if ref.ndim == 1:
        ref = ref[:, None]

    if wave.ndim != 2 or ref.ndim != 2:
        raise ValueError("waveform 和 ref_waveform 必须是 1-D 或 2-D 数组")

    T = wave.shape[0]
    R = wave.shape[1]
    T_ref = ref.shape[0]
    P = ref.shape[1]

    # 如果 T < T_ref，将 waveform 补零到 T_ref 长度
    T_eff = max(T, T_ref)
    if T < T_ref:
        wave = np.pad(wave, ((0, T_ref - T), (0, 0)))

    # 对每个接收天线 r 和参考端口 p 计算互相关
    mag = np.zeros((T_eff, R, P), dtype=float)

    for r in range(R):
        for p in range(P):
            corr = np.correlate(wave[:, r], ref[:, p], mode="full")
            # 取正延迟部分：delay 0 到 T_eff - 1
            start = T_ref - 1
            end = start + T_eff
            seg = np.abs(corr[start:end])
            mag[: len(seg), r, p] = seg

    # 跨端口求和 → [T_eff, R]
    mag_portsum = np.sum(mag, axis=2)
    # 跨天线求和 → [T_eff]
    mag_sum = np.sum(mag_portsum, axis=1)

    # 应用最大延迟窗口
    search_end = len(mag_sum)
    if max_delay is not None and max_delay > 0:
        search_end = min(search_end, max_delay + 1)

    # 在搜索范围内找峰值
    search_region = mag_sum[:search_end]
    peak_index = int(np.argmax(search_region))
    peak_magnitude = float(search_region[peak_index])

    # 应用门限
    if threshold > 0 and peak_magnitude < threshold:
        return None, mag_sum.tolist(), peak_magnitude

    offset = peak_index
    return offset, mag_sum.tolist(), peak_magnitude


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NR Timing Estimate — 5G NR 定时估计",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""调用模式：
  模式 1（直接）：提供 --waveform 和 --ref_waveform
  模式 2（完整）：提供 --waveform、--ref_ind、--ref_sym、--nrb、--scs、--nslot
                 工具内部自动 OFDM 调制生成参考波形

示例：
  # 模式 1：直接输入参考波形
  python tools/nr_timing_estimate.py --waveform '{"real":[[0],[0],[1]],"imag":[[0],[0],[0]]}' \\
      --ref_waveform '{"real":[[1],[0.5]],"imag":[[0],[0]]}'

  # 模式 2：自动生成参考波形
  python tools/nr_timing_estimate.py --waveform '{"real":[...],"imag":[...]}' \\
      --ref_ind [0,144,288] --ref_sym [1,1,1] --nrb 1 --scs 15 --nslot 0
""",
    )

    # 公共参数
    parser.add_argument("--waveform", required=True,
                        help='接收波形 JSON，形状 [T, R] 或 [T]')
    parser.add_argument("--threshold", type=float, default=0.0,
                        help='相关幅度门限 (0..1)，低于此值返回 None，默认 0')
    parser.add_argument("--max_delay", type=int, default=None,
                        help='最大延迟搜索范围（样本数），默认搜索全部')

    # 模式 1：直接输入参考波形
    parser.add_argument("--ref_waveform", default=None,
                        help='[模式1] 参考波形 JSON，形状 [T_ref, P] 或 [T_ref]')

    # 模式 2：自动生成参考波形
    parser.add_argument("--ref_ind", default=None,
                        help='[模式2] 参考信号线性索引 JSON 数组（0-based）')
    parser.add_argument("--ref_sym", default=None,
                        help='[模式2] 参考符号 JSON 数组，单端口 1-D，多端口 [n_ind, P]')
    parser.add_argument("--nrb", type=int, default=None,
                        help='[模式2] 资源块数量')
    parser.add_argument("--scs", type=float, default=None,
                        help='[模式2] 子载波间隔 (kHz)')
    parser.add_argument("--nslot", type=int, default=None,
                        help='[模式2] 初始时隙号（0-based）')
    parser.add_argument("--nsym", type=int, default=14,
                        help='[模式2] 每时隙 OFDM 符号数，默认 14')

    args = parser.parse_args()

    try:
        # 解析接收波形
        waveform = parse_complex(args.waveform)

        # 确定参考波形来源
        if args.ref_waveform is not None:
            # 模式 1：直接使用提供的参考波形
            ref_waveform = parse_complex(args.ref_waveform)
        elif args.ref_ind is not None and args.ref_sym is not None:
            # 模式 2：自动生成参考波形
            if args.nrb is None or args.scs is None or args.nslot is None:
                raise ValueError("模式 2 需要 --nrb、--scs、--nslot")
            ref_ind = json.loads(args.ref_ind)
            ref_sym = json.loads(args.ref_sym)
            ref_waveform = _build_reference_waveform(
                ref_ind, ref_sym, args.nrb, args.scs, args.nslot, args.nsym
            )
        else:
            raise ValueError("必须提供 --ref_waveform（模式1）或 --ref_ind + --ref_sym（模式2）")

        # 执行定时估计
        offset, mag, peak_magnitude = nr_timing_estimate(
            waveform, ref_waveform, args.threshold, args.max_delay
        )

        result = {
            "offset": offset,
            "mag": mag,
            "peak_magnitude": peak_magnitude,
            "mode": "direct" if args.ref_waveform is not None else "generated",
        }
        print(json.dumps(result))

    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
