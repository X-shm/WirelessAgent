"""Build review-only SkillOpt candidates; recompute each reference via local MCP.

The original D/W/H examples remain unchanged. Output stays draft and cannot be
frozen as approved business data without product review.
"""
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
from scripts.build_business_review_draft import draft_specs
from scripts.build_workflow_review_draft import specs as workflow_specs
from scripts.build_independent_holdout_draft import specs as holdout_specs

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "SkillOpt_筛选扩充草案.jsonl.example"
DROP = {"D09", "D12", "D13", "D22", "D25"}


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def one(case_id: str, split: str, tool: str, question: str, args: dict, paths: list[str]) -> dict:
    return dict(id=case_id, split=split, kind="tool_call", tool=tool, question=question,
                arguments=args, answer_paths=paths, source_ref=f"repo:tools/{tool}.schema.json")


def added_specs() -> list[dict]:
    """Two train cases and one selection case per registered product domain."""
    rows = [
        one("A01", "train", "lte_tbs", "LTE 下行分配 12 个 PRB、I_TBS 为 11、单层传输。查表得到的传输块大小是多少比特？",
            {"nprb": 12, "itbs": "11", "smnlayer": 1}, ["/tbs"]),
        one("A02", "train", "lte_modulation", "将 LTE 16QAM 的输入比特 0,0,1,1,1,0,1,0 映射成复符号，列出实部和虚部。",
            {"mod": "16QAM", "bits": "0,0,1,1,1,0,1,0"}, ["/symbols_real", "/symbols_imag"]),
        one("A03", "selection", "lte_prbs", "以 c_init=57 生成长度 12 的 LTE Gold 伪随机比特序列，起点为 0；给出序列。",
            {"cinit": 57, "length": 12, "start": 0, "mapping": "binary"}, ["/sequence"]),
        one("A04", "train", "nr_layer_map", "把四个 5G NR 复符号 1+0.5j、2+1j、3+1.5j、4+2j 映射到两层，给出各层实部和虚部。",
            {"nlayers": 2, "symbols": "[1+0.5j,2+1j,3+1.5j,4+2j]"}, ["/symbols_real", "/symbols_imag"]),
        one("A05", "train", "nr_crc", "给 5G NR 比特 1,0,1,1,0,1,0,0 追加 CRC11，掩码为 0；给出编码后比特。",
            {"poly": "11", "bits": "1,0,1,1,0,1,0,0", "mask": 0, "decode": False}, ["/output_bits"]),
        one("A06", "selection", "nr_pdcch", "一段 5G NR PDCCH 编码码字为 1,0,1,1,0,0,1,0，N_ID=23、N_RNTI=321。完成加扰与 QPSK 调制，给出符号实部和虚部。",
            {"codeword": "1,0,1,1,0,0,1,0", "n-id": 23, "n-rnti": 321}, ["/sym_real", "/sym_imag"]),
        one("A07", "train", "wlan_bcc", "对 WLAN 比特 1,0,1,1,0,0,1,1 使用码率 1/2 的 BCC 编码，给出输出比特。",
            {"bits": "1,0,1,1,0,0,1,1", "rate": "1/2"}, ["/output_bits"]),
        one("A08", "train", "wlan_golay", "为 802.11ad DMG 训练序列生成长度 32 的 Golay 互补序列对，给出 Ga 和 Gb。",
            {"length": 32}, ["/Ga", "/Gb"]),
        one("A09", "selection", "wlan_packet_detect", "对实部为 [0,0,1,1,0,0]、虚部全 0 的短接收波形，以 0.5 门限做 WLAN 包前导检测。是否检测到有效前导？给出判决统计量长度。",
            {"waveform": compact({"real": [0,0,1,1,0,0], "imag": [0]*6}), "threshold": 0.5}, ["/detected", "/n_stats"]),
        one("A10", "train", "ble_gap_data", "在 BLE 广播数据中只编码 Flags 类型，给出数据块十六进制值和字节数。",
            {"input": compact({"operation": "encode", "configuration": {"advertising_data_types": ["Flags"]}})}, ["/result/data_block_hex", "/result/octets"]),
        one("A11", "train", "ble_att", "把属性句柄 0025 的 BLE ATT Read request 编码成 PDU，给出十六进制值和字节数。",
            {"input": compact({"operation": "encode", "configuration": {"opcode": "Read request", "attribute_handle": "0025"}})}, ["/result/pdu_hex", "/result/octets"]),
        one("A12", "selection", "bluetooth_frequency_hop", "Bluetooth BR/EDR 使用 Connection basic 跳频序列、设备地址 2A96EF25，时钟为 2D。计算下一跳信道索引。",
            {"input": compact({"clock": "2D", "configuration": {"sequence_type": "Connection basic", "device_address": "2A96EF25"}})}, ["/result/channel_index"]),
        one("A13", "train", "biterr", "按每元素 3 位比较非负整数序列 [1,4,7] 与 [1,5,3]，给出总比特错误数、误比特率和逐元素错误数。",
            {"x": "[1,4,7]", "y": "[1,5,3]", "k": 3}, ["/num_errors", "/error_ratio", "/individual"]),
        one("A14", "train", "hamming_code", "把消息比特 1,0,1,1 以 m=3 的 Hamming 码编码，给出完整码字。",
            {"mode": "encode", "m": 3, "bits": "1,0,1,1"}, ["/codeword"]),
        one("A15", "selection", "qam_modulation", "将连续比特组 0000、0101、1010、1111 映射到方形 16QAM 星座，给出符号实部和虚部。",
            {"mode": "modulate", "order": 16, "values": "0,0,0,0,0,1,0,1,1,0,1,0,1,1,1,1"}, ["/symbols_real", "/symbols_imag"]),
        one("A16", "train", "node_mobility_random_walk", "离线仿真中节点从 (1,1,0) 米开始，在默认矩形边界内随机游走 4 秒，每秒采样；速度范围 0.5–1.0 米/秒，随机种子 11。给出各时间点和位置。",
            {"initial_position": "1,1,0", "duration": 4, "time_step": 1, "speed_range": "0.5,1.0", "seed": 11}, ["/times", "/positions"]),
        one("A17", "train", "node_mobility_random_waypoint", "离线仿真中节点从 (3,3,0) 米开始，在默认矩形边界内按随机航点移动 4 秒，每秒采样；随机种子 17、无航点暂停。给出时间和位置。",
            {"initial_position": "3,3,0", "duration": 4, "time_step": 1, "pause_duration": 0, "seed": 17}, ["/times", "/positions"]),
        one("A18", "selection", "node_position_random", "在以 (5,5,0) 米为中心的 20×10 米矩形中随机放置 4 个仿真节点，高度 1 米、随机种子 29。给出节点位置。",
            {"boundary_shape": "rectangle", "boundary_dimension": "20,10", "center": "5,5,0", "num_nodes": 4, "z_coordinate": 1, "seed": 29}, ["/positions"]),
        one("A19", "train", "qos_policy_builder", "为一条保底 200 kbps、上限 500 kbps 的直播视频业务生成 5QI 导向的 QoS 初步建议；链路容量 1000 kbps、可承诺比例 0.8。给出建议和容量可行性。",
            {"services": compact([{"id":"live1","service_type":"live_video","guaranteed_kbps":200,"max_kbps":500}]), "link_capacity_kbps": 1000, "reserve_fraction": 0.8}, ["/qos_data", "/capacity_feasible"]),
        one("A20", "train", "resource_allocation_optimizer", "LTE 下行共有 18 个 PRB。三名用户的 (SNR dB,需求 kbps,优先级) 分别为 u1(18,3000,2)、u2(8,1500,1)、u3(3,500,1)。按工具的加权边际 TBS 策略试算分配，并列出每人的需求是否满足。",
            {"users": compact([{"id":"u1","snr_db":18,"demand_kbps":3000,"priority":2},{"id":"u2","snr_db":8,"demand_kbps":1500,"priority":1},{"id":"u3","snr_db":3,"demand_kbps":500,"priority":1}]), "total_prbs": 18}, ["/allocations", "/allocated_prbs"]),
        one("A21", "selection", "closed_loop_validator", "一次外部调整的同口径测量：吞吐由 5.0 到 5.5 Mbps，BER 由 0.001 到 0.004，时延由 25 到 35 ms；约束为 BER≤0.002、时延≤30 ms。仅按数值规则判断是否通过验证、是否建议回滚，并列出违例。",
            {"before": compact({"throughput":5.0,"ber":0.001,"latency_ms":25}), "after": compact({"throughput":5.5,"ber":0.004,"latency_ms":35}), "constraints": compact({"ber":{"max":0.002},"latency_ms":{"max":30}})}, ["/accepted", "/rollback_recommended", "/constraint_violations"]),
        one("A22", "train", "wireless_utils", "调用无线测试助手的 bcc-interleave 子命令：对 16 个比特 0,1,0,1,1,0,0,1,1,1,0,0,1,0,1,0 按 N_CBPS=16、N_BPSC=1 交织，给出输出比特。",
            {"command":"bcc-interleave","bits":"0,1,0,1,1,0,0,1,1,1,0,0,1,0,1,0","ncbps":16,"nbpsc":1}, ["/interleaved_bits"]),
        one("A23", "train", "wireless_utils", "使用无线测试助手的 berawgn 子命令，计算 BPSK 在 Eb/N0=3 dB 时的 AWGN 理论 BER。",
            {"command":"berawgn","ebn0":3,"mod":"bpsk"}, ["/ber"]),
        one("A24", "selection", "wireless_utils", "使用无线测试助手的 biterr 子命令，比较参考比特 1,0,1,0,1,1 与接收比特 1,1,1,0,0,1；给出错误位数和 BER。",
            {"command":"biterr","x":"1,0,1,0,1,1","y":"1,1,1,0,0,1"}, ["/num_errors", "/ber"]),
        {
            "id": "A25", "split": "train", "kind": "tool_workflow",
            "question": "将 0,1,1,0 编成 m=3 的 Hamming 码，再把生成的码字原样送入解码器。给出码字和恢复的消息比特。",
            "source_ref": "repo:tools/hamming_code.schema.json",
            "steps": [
                {"tool": "hamming_code", "arguments": {"mode": "encode", "m": 3, "bits": "0,1,1,0"}},
                {"tool": "hamming_code", "arguments": {"mode": "decode", "m": 3, "bits": None},
                 "bindings": [{"argument": "bits", "from_step": 0, "path": "/codeword", "format": "csv"}]},
            ],
            "answer_fields": {"codeword": {"step": 0, "path": "/codeword"},
                              "message": {"step": 1, "path": "/message"}},
        },
        {
            "id": "A26", "split": "selection", "kind": "tool_workflow",
            "question": "先对 WLAN 比特 0,1,0,0,1,1,0,1,1,0,1,0 用码率 1/2 的 BCC 编码，再将得到的硬判决码字送入 Viterbi 解码器。给出编码比特和解码比特。",
            "source_ref": "repo:tools/wlan_bcc.schema.json",
            "steps": [
                {"tool": "wlan_bcc", "arguments": {"bits": "0,1,0,0,1,1,0,1,1,0,1,0", "rate": "1/2", "decode": False}},
                {"tool": "wlan_bcc", "arguments": {"bits": None, "rate": "1/2", "decode": True},
                 "bindings": [{"argument": "bits", "from_step": 0, "path": "/output_bits", "format": "csv"}]},
            ],
            "answer_fields": {"encoded": {"step": 0, "path": "/output_bits"},
                              "decoded": {"step": 1, "path": "/decoded"}},
        },
        one("A27", "selection", "lte_layer_map", "将 LTE 复数码字符号 (1+0j),(0+1j),(-1+0j),(0-1j) 映射到两层，给出各层的复符号。",
            {"mode": "map", "nlayers": 2,
             "data": compact([{"real": [1.0, 0.0, -1.0, 0.0], "imag": [0.0, 1.0, 0.0, -1.0]}])}, ["/layers"]),
        {
            "id": "A28", "split": "selection", "kind": "tool_workflow",
            "question": "为内部 Bluetooth LE 仿真建立一个新会话，在会话中创建 ID 为 node_a28 的 LE 节点，再列出会话对象。给出新节点的 ID、类型和最终对象列表。",
            "source_ref": "repo:tools/bluetooth_session.schema.json",
            "steps": [
                {"tool": "bluetooth_session", "arguments": {"input": compact({"operation": "create_session", "session_file": "a28_session.sqlite"})}},
                {"tool": "bluetooth_session", "arguments": {"input": compact({"operation": "create_object", "session_file": "a28_session.sqlite", "object_type": "bluetoothLENode", "new_object_id": "node_a28", "properties": {}})}},
                {"tool": "bluetooth_session", "arguments": {"input": compact({"operation": "list_objects", "session_file": "a28_session.sqlite"})}},
            ],
            "answer_fields": {"object_id": {"step": 1, "path": "/result/object_id"},
                              "object_type": {"step": 1, "path": "/result/object_type"},
                              "objects": {"step": 2, "path": "/result/objects"}},
        },
    ]
    assert len(rows) == 28
    return rows


def revise(row: dict) -> None:
    cid = row["id"]
    if cid == "D01":
        row["question"] = "某 LTE 链路测得 SNR 8 dB、EVM 12%、BER 0.003、残余频偏 1800 Hz。按工具内置规则列出触发的劣化因素、证据和建议动作；给出下一步检查，不要求工具判断唯一排查优先级。"
        row["answer_paths"] = ["/status", "/findings", "/recommended_next_tool"]
    elif cid == "D02":
        row["question"] = "LTE 下行链路 SNR 为 15 dB，可用 25 个 PRB，预留 2 dB 裕量，目标 BLER 为 0.1。按工具内置简化模型给出初步链路自适应建议和估算峰值吞吐。"
        row["answer_paths"].append("/estimated_peak_mbps")
    elif cid == "D03":
        row["question"] = "LTE 下行共有 25 个 PRB。u1 的 SNR 为 15 dB、需求 5000 kbps、优先级 2；u2 分别为 5 dB、2000 kbps、优先级 1。按工具的加权边际 TBS 策略试算各人 PRB 和需求是否满足；这是策略模拟，不是现场调度指令。"
    elif cid == "D04":
        row["question"] = "同口径测量下，一次外部调整前吞吐为 10 Mbps、BER 为 0.01、时延为 30 ms；调整后分别为 12 Mbps、0.001、25 ms。数值约束为 BER≤0.002、时延≤30 ms。仅做数值规则核验：是否通过、是否建议回滚？"
    elif cid == "D14":
        row["question"] = row["question"].replace("换算成 SNR", "按每符号 1 个采样点换算成 SNR")
        row["arguments"]["samples_per_symbol"] = 1
    elif cid == "D15":
        row["question"] = "16QAM 每符号 4 比特、编码率 0.75，每符号 1 个采样点；测得 SNR 为 8 dB。换算成 Eb/No 是多少 dB？"
        row["arguments"].update({"input_mode": "snr", "output_mode": "ebno", "samples_per_symbol": 1})
    elif cid == "D18":
        row["question"] = "20 MHz Non-HT WLAN 数据字段在过采样因子 1 时，活跃子载波的频率索引和导频索引分别是什么？"
        row["arguments"]["osf"] = 1
        row["answer_paths"] = ["/ActiveFrequencyIndices", "/PilotIndices"]
    elif cid == "D20":
        row["answer_paths"] = ["/times", "/positions"]
    elif cid == "D21":
        row["question"] = "以 (0,0,0) 米为区域中心，在长 120 米、宽 60 米的矩形内按 2 行 3 列划分网格。请给出六个单元的多边形边界顶点，节点高度设为 0 米。"
        row["arguments"].update({"center": "0,0,0", "z_coordinate": 0})
        row["answer_paths"] = ["/cell_polygons"]
    elif cid == "D23":
        row.update(tool="biterr", source_ref="repo:tools/biterr.schema.json",
                   question="逐位比较参考比特 0,1,1,0,1,0 与接收比特 0,1,0,0,1,1（每元素 1 位），错误位数和误比特率分别是多少？",
                   arguments={"x":"[0,1,1,0,1,0]","y":"[0,1,0,0,1,1]","k":1},
                   answer_paths=["/num_errors","/error_ratio"])
    elif cid == "D24":
        row.update(tool="ber_awgn", source_ref="repo:tools/ber_awgn.schema.json",
                   question="未编码 BPSK 在 AWGN 信道下，Eb/N0 为 6 dB 时的理论 BER 是多少？",
                   arguments={"ebno_db":"6","modulation":"bpsk"}, answer_paths=["/ber"])
    elif cid == "D26":
        row["answer_terms"] = ["PRB", "调制", "码率", "层数", "RE"]
    elif cid == "H05":
        row["question"] = "在当前蓝牙工具的简化测试包模型中，LE 1M、无 CTE、载荷 12 字节且 packet_type=Disabled。计算模型返回的包时长（微秒）和物理层比特数。"
    elif cid == "H13":
        row["question"] = "为无线通信算法测试生成长度 16 的 Golay 互补序列对，给出两条序列。"


def curated_specs() -> list[dict]:
    originals = [*draft_specs(), *workflow_specs(), *holdout_specs()]
    if len(originals) != 48 or len({row["id"] for row in originals}) != 48:
        raise RuntimeError("Original D/W/H inventory changed; review decisions again")
    rows = []
    for row in originals:
        if row["id"] in DROP:
            continue
        revise(row)
        row.setdefault("split", "holdout")
        row.setdefault("kind", "tool_workflow" if "steps" in row else "tool_call")
        row.setdefault("scenario_id", f"curated_{row['id']}")
        rows.append(row)
    rows.extend(added_specs())
    for row in rows:
        row.setdefault("scenario_id", f"curated_{row['id']}")
        row.update(origin_type="expert_authored", reviewer="PENDING_PRODUCT_REVIEW", review_status="draft")
    if len({row["id"] for row in rows}) != len(rows):
        raise RuntimeError("Duplicate case IDs")
    return rows


async def build(output: Path, *, overwrite: bool = False) -> dict:
    if output.exists():
        if not overwrite:
            raise ValueError(f"Refusing to replace existing draft: {output}")
        old = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not old or any(row.get("review_status") != "draft" for row in old):
            raise ValueError("Refusing to replace reviewed or non-draft cases")
    rows = curated_specs()
    with tempfile.TemporaryDirectory(prefix="wireless-curated-skillopt-") as temp:
        data_root = Path(temp).resolve()
        async with Client(create_server(data_root=data_root), read_timeout_seconds=45) as client:
            visible = {tool.name for tool in (await client.list_tools()).tools}
            for row in rows:
                if row["kind"] == "ask_clarification":
                    if row["tool"] not in visible:
                        raise RuntimeError(f"{row['id']}: clarification tool absent")
                    continue
                steps = row["steps"] if row["kind"] == "tool_workflow" else [row]
                results = []
                for index, step in enumerate(steps):
                    if step["tool"] not in visible:
                        raise RuntimeError(f"{row['id']}: tool {step['tool']} absent")
                    arguments = workflow_arguments(step, results) if row["kind"] == "tool_workflow" else step["arguments"]
                    result = await client.call_tool(step["tool"], arguments)
                    if result.is_error or not isinstance(result.structured_content, dict):
                        raise RuntimeError(f"{row['id']}: MCP step {index} failed: {result.content}")
                    step["arguments"] = arguments
                    step["expected"] = canonical_result(result.structured_content, data_root)
                    results.append(step["expected"])
                if row["kind"] == "tool_workflow":
                    for field, spec in row["answer_fields"].items():
                        if not valid_answer_paths(steps[spec["step"]]["expected"], [spec["path"]]):
                            raise RuntimeError(f"{row['id']}: missing answer field {field}")
                elif not valid_answer_paths(row["expected"], row["answer_paths"]):
                    raise RuntimeError(f"{row['id']}: invalid answer_paths")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(compact(row) for row in rows) + "\n", encoding="utf-8")
    return {"output": str(output), "total": len(rows),
            "train": sum(row["split"] == "train" for row in rows),
            "selection": sum(row["split"] == "selection" for row in rows),
            "holdout": sum(row["split"] == "holdout" for row in rows),
            "mcp_calls": sum(len(row["steps"]) if row["kind"] == "tool_workflow" else row["kind"] == "tool_call" for row in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(build(args.output.resolve(), overwrite=args.overwrite)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
