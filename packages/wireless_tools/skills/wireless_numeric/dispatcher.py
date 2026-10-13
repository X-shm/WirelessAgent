"""Wireless numeric skill dispatcher — thin CLI wrapper.

Forwards calls to the original MATLAB-validated tools under tools/.
Does NOT reimplement any algorithm.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
REPO_ROOT = SKILL_DIR.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
PY = sys.executable

# Intent → tool pack. Keep small; LLM chooses from this list only.
PACK: list[dict] = [
    {"tool": "q_function", "topic": "信息论/公式", "when": "Q(x)、Q逆函数、互补误差", "hint": "--mode qfunc --values 0,1,2"},
    {"tool": "ber_awgn", "topic": "误码率", "when": "AWGN 理论 BER（BPSK/QPSK/QAM/PSK/PAM/FSK）", "hint": "--ebno_db 0,5,10 --modulation qpsk"},
    {"tool": "ber_fading", "topic": "误码率", "when": "Rayleigh/Rician 衰落下 BER", "hint": "--ebno_db 0,10 --fading Rayleigh"},
    {"tool": "ber_coding", "topic": "误码率", "when": "编码后 BER 基线对比", "hint": "--ebno_db 0,5 --coding hamming"},
    {"tool": "convert_snr", "topic": "单位换算", "when": "Eb/No、Es/No、SNR、SNRsc 互转", "hint": "--x 10 --input_mode ebno --output_mode esno --bits_per_symbol 2"},
    {"tool": "link_capacity", "topic": "信息论", "when": "香农容量、MIMO 容量上界", "hint": "--snr_db 10 --bandwidth_hz 1e6"},
    {"tool": "qam_modulation", "topic": "调制", "when": "方形 QAM 映射/解映射、星座点", "hint": "--mode modulate --order 16 --values 0,1,1,0"},
    {"tool": "psk_modulation", "topic": "调制", "when": "PSK 映射/解映射", "hint": "--mode modulate --order 8 --values 0,0,1"},
    {"tool": "pam_modulation", "topic": "调制", "when": "PAM 映射/解映射", "hint": "--mode modulate --order 4 --values 0,1"},
    {"tool": "nr_modulation", "topic": "调制/5G", "when": "5G NR 调制/软解调 LLR（BPSK~1024QAM）", "hint": "--mod QPSK --bits 1,1,0,1"},
    {"tool": "biterr", "topic": "统计", "when": "比特错误数与 BER", "hint": "--x 1,0,1,1 --y 1,1,1,0"},
    {"tool": "symerr", "topic": "统计", "when": "符号错误数与 SER", "hint": "--x 1,2,3 --y 1,3,0"},
    {"tool": "awgn", "topic": "信道", "when": "给信号加高斯噪声", "hint": "--signal '[1,1,1,1]' --snr 10"},
    {"tool": "fading_channel", "topic": "信道", "when": "Rayleigh/Rician 衰落信道仿真", "hint": "--signal '[1,1,1,1]' --model rayleigh --seed 1"},
    {"tool": "nr_crc", "topic": "编码/5G", "when": "NR CRC 编解码（6/11/16/24A/24B/24C）", "hint": "--poly 16 --bits 1,0,1,1"},
    {"tool": "nr_ldpc", "topic": "编码/5G", "when": "NR LDPC 编解码（BG1/BG2）", "hint": "--mode encode --bgn 1 --zc 16 --bits 1,0,1,1"},
    {"tool": "nr_polar", "topic": "编码/5G", "when": "NR Polar 编码（DL/UL）", "hint": "--bits 1,0,1,1 --E 128 --mode DL"},
    {"tool": "hamming_code", "topic": "编码", "when": "Hamming 线性分组码编解码", "hint": "--mode encode --m 3 --bits 1,0,1,1"},
    {"tool": "convolutional_codec", "topic": "编码", "when": "卷积码编码/Viterbi 解码", "hint": "--mode encode --bits 1,0,1,1"},
    {"tool": "nr_tbs", "topic": "参数/5G", "when": "5G NR 传输块大小 TBS", "hint": "--modulation QPSK --nlayers 1 --nprb 50 --nre-per-prb 12 --tcr 0.5"},
    {"tool": "lte_tbs", "topic": "参数/LTE", "when": "LTE TBS（NPRB+ITBS）", "hint": "--nprb 25 --itbs 10 --smnlayer 1"},
    {"tool": "lte_mcs", "topic": "参数/LTE", "when": "LTE MCS 查表 ITBS/调制阶数", "hint": "--imcs 17 --table PDSCH"},
    {"tool": "lte_modulation", "topic": "调制/LTE", "when": "LTE 调制/硬解调", "hint": "--mod QPSK --bits 0,0,1,1"},
    {"tool": "ofdm_modulation", "topic": "OFDM", "when": "通用 OFDM 调制/解调、CP", "hint": "--mode modulate --nfft 8 --cp_length 2 --data '{\"real\":[1,0,0,0],\"imag\":[0,0,0,0]}'"},
    {"tool": "lte_ofdm", "topic": "OFDM/LTE", "when": "LTE OFDM 参数/调制/解调", "hint": "--mode info --nrb 50 --cp Normal"},
    {"tool": "nr_ofdm", "topic": "OFDM/5G", "when": "NR OFDM 调制/解调 + windowing", "hint": "--nfft 128 --nrb 1 --grid '[1,0,0,0,0,0,0,0,0,0,0,0]'"},
]

NAME_SET = {item["tool"] for item in PACK}


def list_pack() -> None:
    print(json.dumps({"repo_root": str(REPO_ROOT), "tools": PACK}, ensure_ascii=False, indent=2))


def run_tool(tool: str, rest: list[str]) -> int:
    if tool not in NAME_SET:
        print(json.dumps({"ok": False, "error": f"tool {tool!r} not in numeric pack; see list"}, ensure_ascii=False))
        return 2
    script = TOOLS_DIR / f"{tool}.py"
    if not script.is_file():
        print(json.dumps({"ok": False, "error": f"missing script {script}"}, ensure_ascii=False))
        return 2
    proc = subprocess.run([PY, str(script), *rest], cwd=str(REPO_ROOT))
    return proc.returncode


def show_help(tool: str) -> int:
    if tool not in NAME_SET:
        print(json.dumps({"ok": False, "error": f"unknown tool {tool!r}"}, ensure_ascii=False))
        return 2
    return subprocess.run([PY, str(TOOLS_DIR / f"{tool}.py"), "--help"], cwd=str(REPO_ROOT)).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Wireless numeric skill dispatcher (wraps tools/*.py)")
    parser.add_argument("action", choices=["list", "run", "help"])
    parser.add_argument("tool", nargs="?", default=None)
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.action == "list":
        list_pack()
        return 0
    if not args.tool:
        print(json.dumps({"ok": False, "error": "tool name required"}, ensure_ascii=False))
        return 2
    rest = args.rest
    if rest and rest[0] == "--":
        rest = rest[1:]
    if args.action == "help":
        return show_help(args.tool)
    return run_tool(args.tool, rest)


if __name__ == "__main__":
    raise SystemExit(main())
