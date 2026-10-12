"""Deterministic radio-link impairment diagnosis for OpenClaw workflows."""
from __future__ import annotations
import argparse
import json


def diagnose(snr_db=None, evm_percent=None, ber=None, bler=None, frequency_offset_hz=None, timing_offset_samples=None, cp_samples=None, delay_spread_samples=None, target_snr_db=10.0, subcarrier_spacing_hz=15000.0):
    findings = []
    def add(cause, severity, evidence, actions):
        findings.append({"cause": cause, "severity": severity, "evidence": evidence, "actions": actions})
    if snr_db is not None and snr_db < target_snr_db:
        gap = target_snr_db-snr_db
        add("noise_or_interference", "critical" if gap > 8 else "warning", {"snr_gap_db": gap}, ["降低 MCS", "检查同频干扰与接收功率", "增加测量样本后重新估计信道"])
    if frequency_offset_hz is not None:
        ratio = abs(frequency_offset_hz)/subcarrier_spacing_hz
        if ratio > 0.03:
            add("carrier_frequency_offset", "critical" if ratio > 0.15 else "warning", {"normalized_offset": ratio}, ["执行 lte_frequency_sync", "检查本振和多普勒补偿"])
    if timing_offset_samples is not None and cp_samples:
        ratio = abs(timing_offset_samples)/cp_samples
        if ratio > 0.25:
            add("timing_misalignment", "critical" if ratio >= 1 else "warning", {"offset_to_cp_ratio": ratio}, ["执行 lte_frame_offset/signal_timing_estimate", "将 FFT 窗移回 CP 内"])
    if delay_spread_samples is not None and cp_samples and delay_spread_samples > 0.8*cp_samples:
        add("excess_delay_spread", "critical" if delay_spread_samples > cp_samples else "warning", {"delay_to_cp_ratio": delay_spread_samples/cp_samples}, ["检查 EPA/EVA/ETU 场景", "增强均衡或调整小区覆盖"])
    if evm_percent is not None and evm_percent > 8:
        cause = "nonlinear_or_phase_impairment" if snr_db is not None and snr_db >= target_snr_db else "poor_signal_quality"
        add(cause, "critical" if evm_percent > 17.5 else "warning", {"evm_percent": evm_percent}, ["检查功放压缩、相噪和 IQ 失衡", "运行 evm_metrics 并按层/子带定位"])
    if ber is not None and ber > 1e-3:
        add("high_bit_error_rate", "critical" if ber > 1e-2 else "warning", {"ber": ber}, ["降低 MCS", "检查软解调、扰码和编码链"])
    if bler is not None and bler > 0.1:
        add("high_block_error_rate", "critical" if bler > 0.3 else "warning", {"bler": bler}, ["增加链路裕量", "检查 HARQ 与资源分配"])
    order = {"ok": 0, "warning": 1, "critical": 2}
    overall = max((item["severity"] for item in findings), key=order.get, default="ok")
    return {"status": overall, "finding_count": len(findings), "findings": findings, "recommended_next_tool": findings[0]["actions"][0] if findings else "保持配置并继续监测"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snr_db", type=float)
    parser.add_argument("--evm_percent", type=float)
    parser.add_argument("--ber", type=float)
    parser.add_argument("--bler", type=float)
    parser.add_argument("--frequency_offset_hz", type=float)
    parser.add_argument("--timing_offset_samples", type=float)
    parser.add_argument("--cp_samples", type=float)
    parser.add_argument("--delay_spread_samples", type=float)
    parser.add_argument("--target_snr_db", type=float, default=10.0)
    parser.add_argument("--subcarrier_spacing_hz", type=float, default=15000.0)
    args = parser.parse_args()
    print(json.dumps(diagnose(**vars(args)), ensure_ascii=False))


if __name__ == "__main__":
    main()
