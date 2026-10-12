"""Build a review-only JSONL draft from repository workflow examples via local MCP."""

from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
from pathlib import Path

from mcp.client import Client

from mcp_server.server import create_server
from skillopt_wireless.build_dataset import canonical_result
from skillopt_wireless.scoring import valid_answer_paths


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "skillopt_review" / "SkillOpt_候选业务题标注.jsonl.example"


def draft_specs() -> list[dict]:
    workflow = "repo:references/network_optimization_workflow.md"
    base = [
        {
            "id": "D01", "split": "train", "tool": "radio_link_diagnosis",
            "question": "某 LTE 链路测得 SNR 8 dB、EVM 12%、BER 0.003、频偏 1800 Hz。请判断主要劣化因素，并说明排查的优先顺序。",
            "arguments": {"snr_db": 8, "evm_percent": 12, "ber": 0.003, "frequency_offset_hz": 1800},
            "answer_paths": ["/status", "/findings"], "source_ref": workflow,
        },
        {
            "id": "D02", "split": "selection", "tool": "link_adaptation_optimizer",
            "question": "链路 SNR 为 15 dB，可用 25 个 PRB，预留 2 dB 裕量，目标 BLER 为 0.1。请给出链路自适应建议。",
            "arguments": {"snr_db": 15, "nprb": 25, "margin_db": 2, "bler_target": 0.1},
            "answer_paths": ["/recommended_mcs", "/modulation", "/tbs_bits_per_subframe"], "source_ref": workflow,
        },
        {
            "id": "D03", "split": "holdout", "tool": "resource_allocation_optimizer",
            "question": "两个用户分别有 SNR 15 dB、需求 5000 kbps、优先级 2，和 SNR 5 dB、需求 2000 kbps、优先级 1；共有 25 个 PRB。怎样分配资源，各自需求能否满足？",
            "arguments": {"users": json.dumps([
                {"id": "u1", "snr_db": 15, "demand_kbps": 5000, "priority": 2},
                {"id": "u2", "snr_db": 5, "demand_kbps": 2000, "priority": 1},
            ], separators=(",", ":")), "total_prbs": 25},
            "answer_paths": ["/allocations", "/allocated_prbs"], "source_ref": workflow,
        },
        {
            "id": "D04", "split": "train", "tool": "closed_loop_validator",
            "question": "调整前吞吐 10、BER 0.01、时延 30 ms；调整后吞吐 12、BER 0.001、时延 25 ms。约束为 BER 不超过 0.002、时延不超过 30 ms。此次调整是否应验收，是否建议回滚？",
            "arguments": {
                "before": json.dumps({"throughput": 10, "ber": 0.01, "latency_ms": 30}, separators=(",", ":")),
                "after": json.dumps({"throughput": 12, "ber": 0.001, "latency_ms": 25}, separators=(",", ":")),
                "constraints": json.dumps({"ber": {"max": 0.002}, "latency_ms": {"max": 30}}, separators=(",", ":")),
            },
            "answer_paths": ["/accepted", "/rollback_recommended"], "source_ref": workflow,
        },
        {
            "id": "D05", "split": "selection", "tool": "nr_tbs",
            "question": "5G NR 下行使用 QPSK、单层、40 个 PRB、每 PRB 132 个 RE、目标码率 0.48。该资源分配的传输块大小是多少比特？",
            "arguments": {"modulation": "QPSK", "nlayers": 1, "nprb": 40, "nre-per-prb": 132, "tcr": 0.48},
            "answer_paths": ["/tbs"], "source_ref": "repo:tools/nr_tbs.schema.json",
        },
        {
            "id": "D06", "split": "holdout", "tool": "nr_mcs_tables",
            "question": "5G NR 的 QAM256 MCS 表中，索引 17 对应什么调制阶数、目标码率和频谱效率？",
            "arguments": {"table": "QAM256Table", "mcs": 17},
            "answer_paths": ["/qm", "/target_code_rate", "/spectral_efficiency"],
            "source_ref": "repo:tools/nr_mcs_tables.schema.json",
        },
        {
            "id": "D07", "split": "train", "tool": "bluetooth_path_loss",
            "question": "在 Industrial 环境，蓝牙设备相距 2 米和 15 米，暂不考虑随机阴影衰落。两处的路径损耗各是多少？",
            "arguments": {"input": json.dumps({"distance": [2, 15], "environment": "Industrial", "standard_deviation": 0}, separators=(",", ":"))},
            "answer_paths": ["/result/path_loss_db"], "source_ref": "repo:tools/bluetooth_path_loss.schema.json",
        },
        {
            "id": "D08", "split": "selection", "tool": "bluetooth_range",
            "question": "我想估算蓝牙链路的覆盖距离。",
            "kind": "ask_clarification", "answer_terms": ["环境", "发射功率", "接收灵敏度"],
            "source_ref": "repo:tools/bluetooth_range.schema.json",
        },
        {
            "id": "D09", "split": "holdout", "tool": "ble_pcap_writer",
            "question": "把这个 BLE Link Layer 数据包 D6BE898E4009AB8967452301020106A8F1DF（时间戳 0 微秒）保存为 PCAPNG 文件，并告诉我生成的文件位置。",
            "arguments": {"input": json.dumps({"file_extension": "pcapng", "packets": [
                {"packet": "D6BE898E4009AB8967452301020106A8F1DF", "timestamp_us": 0}
            ], "output_path": "d09.pcapng"}, separators=(",", ":"))},
            "answer_paths": ["/result/output_path"], "source_ref": "repo:tools/ble_pcap_writer.schema.json",
        },
    ]
    return base + coverage_specs()


def coverage_specs() -> list[dict]:
    """Add representative cases so every registry product appears in each split."""
    def one(case_id: str, split: str, tool: str, question: str, arguments: dict, paths: list[str]) -> dict:
        return {
            "id": case_id, "split": split, "tool": tool,
            "question": question, "arguments": arguments,
            "answer_paths": paths, "source_ref": f"repo:tools/{tool}.schema.json",
        }

    return [
        one("D10", "train", "nr_mcs_tables", "5G NR 的 QAM64 MCS 表中，索引 9 的调制方式和目标码率是什么？",
            {"table": "QAM64Table", "mcs": 9}, ["/modulation", "/target_code_rate"]),
        one("D11", "train", "lte_mcs", "LTE PDSCH 的 MCS 索引 5 对应什么调制方式和 TBS 索引？",
            {"imcs": "5", "table": "PDSCH"}, ["/mod", "/itbs"]),
        one("D12", "selection", "lte_mcs", "LTE PDSCH 的 MCS 索引 12 对应什么调制方式和 TBS 索引？",
            {"imcs": "12", "table": "PDSCH"}, ["/mod", "/itbs"]),
        one("D13", "holdout", "lte_mcs", "LTE PDSCHTable2 的 MCS 索引 23 对应什么调制方式和 TBS 索引？",
            {"imcs": "23", "table": "PDSCHTable2"}, ["/mod", "/itbs"]),
        one("D14", "train", "convert_snr", "链路 Eb/No 为 5 dB，QPSK 每符号 2 比特、编码率 0.5。换算成 SNR 是多少 dB？",
            {"x": "5", "input_mode": "ebno", "output_mode": "snr", "bits_per_symbol": 2, "coding_rate": 0.5}, ["/values_db"]),
        one("D15", "selection", "convert_snr", "链路 Eb/No 为 8 dB，16QAM 每符号 4 比特、编码率 0.75。对应 SNR 是多少 dB？",
            {"x": "8", "input_mode": "ebno", "output_mode": "snr", "bits_per_symbol": 4, "coding_rate": 0.75}, ["/values_db"]),
        one("D16", "holdout", "convert_snr", "64QAM 每符号 6 比特且不编码，Es/No 为 12 dB。请换算成 Eb/No。",
            {"x": "12", "input_mode": "esno", "output_mode": "ebno", "bits_per_symbol": 6, "coding_rate": 1}, ["/values_db"]),
        one("D17", "train", "wlan_scramble", "用初始状态 37 对 WLAN 数据比特 1,0,1,0,1,1,0,0 加扰，输出比特序列是什么？",
            {"bits": "1,0,1,0,1,1,0,0", "seed": 37}, ["/output_bits"]),
        one("D18", "selection", "wlan_ofdm_info", "20 MHz Non-HT WLAN 数据字段的 FFT 长度、采样率和循环前缀长度是多少？",
            {"field": "NonHT-Data", "chanbw": "CBW20"}, ["/FFTLength", "/SampleRate", "/CPLength"]),
        one("D19", "holdout", "wlan_scramble", "已知 WLAN 扰码器初始状态为 93，请对接收比特 1,1,0,0,0,1,0,0 解扰并给出恢复序列。",
            {"bits": "1,1,0,0,0,1,0,0", "seed": 93, "descramble": True}, ["/output_bits"]),
        one("D20", "train", "node_mobility_constant_velocity", "无线节点初始位置为 (0,0,0) 米，速度为 (3,4,0) 米每秒。0、1、5 秒时的位置分别是什么？",
            {"initial_position": "0,0,0", "velocity": "3,4,0", "times": "0,1,5"}, ["/positions"]),
        one("D21", "selection", "node_position_grid", "在长 120 米、宽 60 米的区域内按 2 行 3 列网格中心放置节点，请给出各节点三维位置。",
            {"boundary_dimension": "120,60", "grid_size": "2,3", "placement_type": "center"}, ["/positions"]),
        one("D22", "holdout", "node_mobility_constant_velocity", "无线节点初始位置为 (10,5,0) 米，以 (-1,2,0) 米每秒移动。0、4、8 秒时分别在哪里？",
            {"initial_position": "10,5,0", "velocity": "-1,2,0", "times": "0,4,8"}, ["/positions"]),
        one("D23", "train", "wireless_utils", "参考比特为 0,1,1,0,1,0，接收比特为 0,1,0,0,1,1。共有多少比特错误，BER 是多少？",
            {"command": "biterr", "x": "0,1,1,0,1,0", "y": "0,1,0,0,1,1"}, ["/num_errors", "/ber"]),
        one("D24", "selection", "wireless_utils", "BPSK 在 AWGN 信道下 Eb/N0 为 6 dB，理论 BER 是多少？",
            {"command": "berawgn", "ebn0": 6, "mod": "bpsk"}, ["/ber"]),
        one("D25", "holdout", "wireless_utils", "参考比特为 1,0,1,1,0,0,1,1，接收比特为 1,1,1,0,0,0,1,1。误比特数和 BER 各是多少？",
            {"command": "biterr", "x": "1,0,1,1,0,0,1,1", "y": "1,1,1,0,0,0,1,1"}, ["/num_errors", "/ber"]),
        {
            "id": "D26", "split": "holdout", "tool": "nr_tbs", "kind": "ask_clarification",
            "question": "请帮我计算这次 5G NR 下行的传输块大小。",
            "answer_terms": ["PRB", "调制", "码率"],
            "source_ref": "repo:tools/nr_tbs.schema.json",
        },
    ]


async def build(output: Path, *, overwrite: bool = False) -> dict:
    if output.exists():
        if not overwrite:
            raise ValueError(f"Refusing to replace existing draft: {output}")
        try:
            previous = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Refusing to replace an unreadable draft: {output}") from exc
        if not previous or any(not isinstance(row, dict) or row.get("review_status") != "draft" for row in previous):
            raise ValueError(f"Refusing to replace reviewed or non-draft cases: {output}")
    rows = draft_specs()
    failure = None
    with tempfile.TemporaryDirectory(prefix="wireless-business-draft-") as temp:
        data_root = Path(temp).resolve()
        if not data_root.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError("Temporary MCP data directory is outside the intended root")
        async with Client(create_server(data_root=data_root), read_timeout_seconds=45) as client:
            visible = {tool.name for tool in (await client.list_tools()).tools}
            for row in rows:
                if row["tool"] not in visible:
                    failure = f"{row['id']}: MCP tool is not visible"
                    break
                if row.get("kind") == "ask_clarification":
                    continue
                result = await client.call_tool(row["tool"], row["arguments"])
                if result.is_error or not isinstance(result.structured_content, dict):
                    failure = f"{row['id']}: MCP reference call failed: {result.content}"
                    break
                row["expected"] = canonical_result(result.structured_content, data_root)
                if not valid_answer_paths(row["expected"], row["answer_paths"]):
                    failure = f"{row['id']}: answer_paths do not exist in MCP result; result={json.dumps(row['expected'], ensure_ascii=False)[:500]}"
                    break
    if failure:
        raise RuntimeError(failure)
    for row in rows:
        row.setdefault("kind", "tool_call")
        row["scenario_id"] = f"draft_{row['id']}"
        row["origin_type"] = "expert_authored"
        row["reviewer"] = "PENDING_BUSINESS_REVIEW"
        row["review_status"] = "draft"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return {"output": str(output), "count": len(rows), "mcp_verified": sum(row["kind"] == "tool_call" for row in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true", help="Replace a previous generated draft")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(build(args.output.resolve(), overwrite=args.overwrite)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
