"""Generate review-only two-tool cases with results recomputed by local MCP."""

from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
from pathlib import Path

from mcp.client import Client

from mcp_server.server import create_server
from skillopt_wireless.build_dataset import canonical_result
from skillopt_wireless.scoring import valid_answer_paths, workflow_arguments


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "skillopt_review" / "SkillOpt_多工具候选题.jsonl.example"


def specs() -> list[dict]:
    return [
        {
            "id": "W01", "split": "train", "scenario_id": "workflow_lte_mcs_tbs_train",
            "question": "LTE PDSCH 使用 PDSCH MCS 表，MCS 索引为 18、分配 18 个 PRB、单层传输。请先查出调制方式和 I_TBS，再依据查得的 I_TBS 计算传输块大小（比特）。",
            "source_ref": "repo:tools/lte_mcs.schema.json",
            "steps": [
                {"tool": "lte_mcs", "arguments": {"imcs": "18", "table": "PDSCH"}},
                {"tool": "lte_tbs", "arguments": {"nprb": 18, "itbs": None, "smnlayer": 1},
                 "bindings": [{"argument": "itbs", "from_step": 0, "path": "/itbs", "format": "string"}]},
            ],
            "answer_fields": {
                "mod": {"step": 0, "path": "/mod"},
                "itbs": {"step": 0, "path": "/itbs"},
                "tbs": {"step": 1, "path": "/tbs"},
            },
        },
        {
            "id": "W02", "split": "selection", "scenario_id": "workflow_nr_mcs_tbs_selection",
            "question": "5G NR 采用 QAM256 MCS 表的索引 21、32 个 PRB、每 PRB 132 个 RE、单层传输。请先查调制方式和目标码率，再用查得的值计算传输块大小（比特）。",
            "source_ref": "repo:tools/nr_mcs_tables.schema.json",
            "steps": [
                {"tool": "nr_mcs_tables", "arguments": {"table": "QAM256Table", "mcs": 21}},
                {"tool": "nr_tbs", "arguments": {"modulation": None, "nlayers": 1, "nprb": 32,
                                                 "nre-per-prb": 132, "tcr": None},
                 "bindings": [
                     {"argument": "modulation", "from_step": 0, "path": "/modulation"},
                     {"argument": "tcr", "from_step": 0, "path": "/target_code_rate"},
                 ]},
            ],
            "answer_fields": {
                "modulation": {"step": 0, "path": "/modulation"},
                "target_code_rate": {"step": 0, "path": "/target_code_rate"},
                "tbs": {"step": 1, "path": "/tbs"},
            },
        },
        {
            "id": "W03", "split": "holdout", "scenario_id": "workflow_snr_ber_holdout",
            "question": "未编码 16QAM 的 Es/N0 为 11 dB。请先按每符号 4 比特换算 Eb/N0，再计算 AWGN 信道下的理论 BER，并给出两个数值。",
            "source_ref": "repo:tools/convert_snr.schema.json",
            "steps": [
                {"tool": "convert_snr", "arguments": {"x": "11", "input_mode": "esno",
                                                       "output_mode": "ebno", "bits_per_symbol": 4,
                                                       "coding_rate": 1}},
                {"tool": "ber_awgn", "arguments": {"ebno_db": None, "modulation": "qam", "order": 16},
                 "bindings": [{"argument": "ebno_db", "from_step": 0,
                               "path": "/values_db", "format": "string"}]},
            ],
            "answer_fields": {
                "values_db": {"step": 0, "path": "/values_db"},
                "ber": {"step": 1, "path": "/ber"},
            },
        },
        {
            "id": "W04", "split": "train", "scenario_id": "workflow_lte_diagnose_validate_train",
            "question": "某 LTE 链路测得 SNR 9 dB、EVM 8%、BER 0.0008、残余频偏 200 Hz。可用 30 个 PRB，预留 1 dB 裕量，目标 BLER 0.05。请先诊断链路，再给出链路自适应初步建议。一次由外部人员完成的调整，在相同口径下测得调整前吞吐 3.0 Mbps、BER 0.003、时延 27 ms；调整后吞吐 4.0 Mbps、BER 0.0005、时延 24 ms。约束为 BER 不超过 0.001、时延不超过 25 ms。请核验这组前后数据并说明是否建议回滚。",
            "source_ref": "repo:references/network_optimization_workflow.md",
            "steps": [
                {"tool": "radio_link_diagnosis", "arguments": {"snr_db": 9, "evm_percent": 8,
                                                                 "ber": 0.0008, "frequency_offset_hz": 200}},
                {"tool": "link_adaptation_optimizer", "arguments": {"snr_db": 9, "nprb": 30,
                                                                     "margin_db": 1, "bler_target": 0.05}},
                {"tool": "closed_loop_validator", "arguments": {
                    "before": json.dumps({"throughput": 3.0, "ber": 0.003, "latency_ms": 27}, separators=(",", ":")),
                    "after": json.dumps({"throughput": 4.0, "ber": 0.0005, "latency_ms": 24}, separators=(",", ":")),
                    "constraints": json.dumps({"ber": {"max": 0.001}, "latency_ms": {"max": 25}}, separators=(",", ":")),
                }},
            ],
            "answer_fields": {
                "status": {"step": 0, "path": "/status"},
                "findings": {"step": 0, "path": "/findings"},
                "recommended_mcs": {"step": 1, "path": "/recommended_mcs"},
                "accepted": {"step": 2, "path": "/accepted"},
                "rollback_recommended": {"step": 2, "path": "/rollback_recommended"},
            },
        },
    ]


async def build(output: Path, *, overwrite: bool = False) -> dict:
    if output.exists():
        if not overwrite:
            raise ValueError(f"Refusing to replace existing draft: {output}")
        try:
            old = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Refusing to replace unreadable draft: {output}") from exc
        if not old or any(not isinstance(row, dict) or row.get("review_status") != "draft" for row in old):
            raise ValueError(f"Refusing to replace reviewed or non-draft cases: {output}")
    rows = specs()
    with tempfile.TemporaryDirectory(prefix="wireless-workflow-draft-") as temp:
        data_root = Path(temp).resolve()
        async with Client(create_server(data_root=data_root), read_timeout_seconds=45) as client:
            visible = {tool.name for tool in (await client.list_tools()).tools}
            for row in rows:
                prior_results = []
                for index, step in enumerate(row["steps"]):
                    if step["tool"] not in visible:
                        raise RuntimeError(f"{row['id']}: step {index} tool is not visible")
                    arguments = workflow_arguments(step, prior_results)
                    result = await client.call_tool(step["tool"], arguments)
                    if result.is_error or not isinstance(result.structured_content, dict):
                        raise RuntimeError(f"{row['id']}: step {index} reference MCP call failed")
                    actual = canonical_result(result.structured_content, data_root)
                    step["arguments"] = arguments
                    step["expected"] = actual
                    prior_results.append(actual)
                for field, spec in row["answer_fields"].items():
                    if not valid_answer_paths(row["steps"][spec["step"]]["expected"], [spec["path"]]):
                        raise RuntimeError(f"{row['id']}: answer field {field} is absent")
    for row in rows:
        row.update(kind="tool_workflow", origin_type="expert_authored",
                   reviewer="PENDING_BUSINESS_REVIEW", review_status="draft")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return {"output": str(output), "cases": len(rows), "mcp_calls": sum(len(row["steps"]) for row in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(build(args.output.resolve(), overwrite=args.overwrite)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
