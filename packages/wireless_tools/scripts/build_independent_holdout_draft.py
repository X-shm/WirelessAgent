"""Build a review-only holdout draft, recomputing every reference with local MCP."""

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
DEFAULT_OUTPUT = ROOT / "docs" / "skillopt_review" / "SkillOpt_独立验收候选题.jsonl.example"


def compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def one(case_id: str, tool: str, question: str, arguments: dict,
        answer_paths: list[str], *, source_ref: str | None = None) -> dict:
    return {
        "id": case_id, "kind": "tool_call", "tool": tool, "question": question,
        "arguments": arguments, "answer_paths": answer_paths,
        "source_ref": source_ref or f"repo:tools/{tool}.schema.json",
    }


def specs() -> list[dict]:
    channels = [3, 4, 9, 10, 21, 22, 33, 34]
    return [
        one("H01", "lte_cqi_select",
            "LTE Port0 链路三个子带的 SINR 分别为 2、8、14 dB。按内置门限生成 Subband CQI 报告，给出宽带 CQI 和各子带 CQI。",
            {"sinr_db": "[2,8,14]", "tx_scheme": "Port0", "reporting": "Subband"},
            ["/wideband_cqi", "/subband_cqi"]),
        one("H02", "lte_crc",
            "给 LTE 比特 1,0,1,1,0,0,1,0 追加 CRC8，掩码为 0。请给出 CRC 校验位及追加后的完整比特序列。",
            {"poly": "8", "bits": "1,0,1,1,0,0,1,0", "mask": 0, "verify": False},
            ["/parity", "/crc"]),
        {
            "id": "H03", "kind": "tool_workflow",
            "question": "用初始化值 2077 生成 12 位 5G NR PRBS，再对这 12 位依次追加 NR CRC6。请给出原序列和编码后的比特序列。",
            "source_ref": "repo:tools/nr_prbs.schema.json",
            "steps": [
                {"tool": "nr_prbs", "arguments": {"cinit": 2077, "n": 12, "mapping": "binary"}},
                {"tool": "nr_crc", "arguments": {"poly": "6", "bits": None, "mask": 0, "decode": False},
                 "bindings": [{"argument": "bits", "from_step": 0, "path": "/seq", "format": "csv"}]},
            ],
            "answer_fields": {"seq": {"step": 0, "path": "/seq"},
                              "output_bits": {"step": 1, "path": "/output_bits"}},
        },
        one("H04", "nr_modulation",
            "将 NR QPSK 比特 0,0,1,0,1,1,0,1 调制成复符号，给出各符号的实部和虚部。",
            {"mod": "QPSK", "bits": "0,0,1,0,1,1,0,1", "inverse": False},
            ["/symbols_real", "/symbols_imag"]),
        one("H05", "bluetooth_packet_duration",
            "一个无 CTE 的 Bluetooth LE 1M 数据包，载荷为 12 字节。按工具的 Disabled 包类型计算包时长（微秒）和物理层比特数。",
            {"input": compact({"mode": "LE1M", "packet_type": "Disabled", "payload_length": 12})},
            ["/result/duration_us", "/result/num_bits"]),
        {
            "id": "H06", "kind": "tool_workflow",
            "question": "Bluetooth LE 使用 CSA #2、默认接入地址，数据信道集合为 3、4、9、10、21、22、33、34。先计算前 2 个连接事件，再沿用返回状态计算后 2 个事件。给出后 2 个事件的信道索引和最后的事件计数。",
            "source_ref": "repo:tools/ble_channel_selection.schema.json",
            "steps": [
                {"tool": "ble_channel_selection", "arguments": {
                    "input": compact({"algorithm": 2, "used_channels": channels, "count": 2})}},
                {"tool": "ble_channel_selection", "arguments": {"input": compact({"count": 2}), "state": None},
                 "bindings": [{"argument": "state", "from_step": 0, "path": "/state", "format": "json"}]},
            ],
            "answer_fields": {"channel_indices": {"step": 1, "path": "/result/channel_indices"},
                              "event_counter": {"step": 1, "path": "/result/event_counter"}},
        },
        one("H07", "q_function", "计算标准高斯 Q 函数在 0 和 1.5 处的值，按输入顺序给出。",
            {"mode": "qfunc", "values": "0,1.5"}, ["/output"]),
        one("H08", "bit_int_conversion",
            "把整数 3、5、6 分别转为固定 3 位比特组，组内使用 LSB-first 位序。请给出转换后的比特。",
            {"mode": "int_to_bit", "values": "3,5,6", "width": 3, "bit_order": "lsbfirst"},
            ["/values"]),
        one("H09", "wlan_ofdm_info",
            "查询 10 MHz Non-HT WLAN 的 L-LTF 字段：FFT 长度、采样率（Hz）和循环前缀长度（采样点）分别是多少？过采样因子为 1。",
            {"field": "L-LTF", "chanbw": "CBW10", "osf": 1},
            ["/FFTLength", "/SampleRate", "/CPLength"]),
        one("H10", "wlan_constellation",
            "将 WLAN 每子载波 4 比特的序列 0,1,1,0,1,0,0,1 做星座映射。请给出复符号的实部和虚部。",
            {"mode": "map", "num_bpscs": 4, "bits": "0,1,1,0,1,0,0,1"},
            ["/symbols_real", "/symbols_imag"]),
        one("H11", "wireless_packet",
            "为离线无线网络仿真建立一条包记录：发射节点 7，位置 (1,2,0) 米，速度 (0,0,0) 米每秒，开始时间 0.01 秒，时长 0.002 秒，功率 15 dBm，中心频率 2.4 GHz，带宽 20 MHz，数据为 [1,0,1]，其余属性采用工具默认值。给出创建后记录中的节点 ID、功率和数据字段。",
            {"transmitter_id": 7, "transmitter_position": "1,2,0", "transmitter_velocity": "0,0,0",
             "start_time": 0.01, "duration": 0.002, "power": 15,
             "center_frequency": 2400000000, "bandwidth": 20000000, "data": "[1,0,1]"},
            ["/TransmitterID", "/Power", "/Data"]),
        one("H12", "node_position_grid",
            "以 (10,20,0) 米为中心的 40×20 米矩形区域，按 2 行 2 列网格的单元中心放置节点，高度为 1.5 米，每格 1 个。给出四个节点位置。",
            {"boundary_dimension": "40,20", "center": "10,20,0", "grid_size": "2,2",
             "placement_type": "center", "z_coordinate": 1.5, "num_nodes_per_cell": 1},
            ["/positions"]),
        one("H13", "wireless_utils",
            "使用 WirelessAgent Helper 的 wireless_utils 工具中 golay 子命令，生成长度 16 的 Golay 互补序列对。给出两条序列。",
            {"command": "golay", "length": 16}, ["/Ga", "/Gb"]),
        {
            "id": "H14", "kind": "tool_workflow",
            "question": "为一个语音业务（保底 120 kbps、上限 240 kbps）和一个游戏业务（保底 300 kbps、上限 500 kbps）生成 5QI 导向的 QoS 建议。可用链路容量 1500 kbps，其中 80% 可承诺。再把生成的 QoS 数据交给策略校验器做容量和规则检查；目前没有实测 KPI。给出容量可行性、规则校验是否通过及工具返回的回滚标志，不把它当作现场效果验收。",
            "source_ref": "repo:tools/qos_policy_builder.schema.json",
            "steps": [
                {"tool": "qos_policy_builder", "arguments": {
                    "services": compact([
                        {"id": "voice1", "service_type": "voice", "guaranteed_kbps": 120, "max_kbps": 240},
                        {"id": "game1", "service_type": "gaming", "guaranteed_kbps": 300, "max_kbps": 500},
                    ]), "link_capacity_kbps": 1500, "reserve_fraction": 0.8}},
                {"tool": "policy_decision_validator", "arguments": {
                    "qos_data": None, "link_capacity_kbps": 1500, "reserve_fraction": 0.8},
                 "bindings": [{"argument": "qos_data", "from_step": 0, "path": "/qos_data", "format": "json"}]},
            ],
            "answer_fields": {"capacity_feasible": {"step": 0, "path": "/capacity_feasible"},
                              "accepted": {"step": 1, "path": "/accepted"},
                              "rollback_recommended": {"step": 1, "path": "/rollback_recommended"}},
        },
        one("H15", "traffic_steering_optimizer",
            "一个 500 kbps、最多 30 ms 时延的业务流，可选接入 A（容量 1000 kbps、时延 40 ms、SNR 20 dB）与 B（容量 900 kbps、时延 20 ms、SNR 12 dB）。滞回设为 0.05。请给出分流结果和未满足的业务流数。",
            {"flows": compact([{"id": "f1", "required_kbps": 500, "max_latency_ms": 30}]),
             "accesses": compact([{"id": "A", "capacity_kbps": 1000, "latency_ms": 40, "snr_db": 20},
                                  {"id": "B", "capacity_kbps": 900, "latency_ms": 20, "snr_db": 12}]),
             "hysteresis": 0.05},
            ["/assignments", "/unserved_flow_count"]),
        one("H16", "link_capacity",
            "仅作 SISO Shannon 理论上界估算：接收 SNR 为 10 dB、带宽 5 MHz。频谱效率和容量上界分别是多少？",
            {"snr_db": 10, "bandwidth_hz": 5000000},
            ["/spectral_efficiency_bps_hz", "/capacity_bps"]),
        {"id": "H17", "kind": "ask_clarification", "tool": "lte_crc",
         "question": "请帮我给这段 LTE 数据追加 CRC。", "answer_terms": ["数据比特", "CRC多项式"],
         "source_ref": "repo:tools/lte_crc.schema.json"},
        {"id": "H18", "kind": "ask_clarification", "tool": "bluetooth_packet_duration",
         "question": "这个蓝牙包的发送时长是多少？", "answer_terms": ["模式", "包类型", "载荷长度"],
         "source_ref": "repo:tools/bluetooth_packet_duration.schema.json"},
    ]


async def build(output: Path, *, overwrite: bool = False) -> dict:
    if output.exists():
        if not overwrite:
            raise ValueError(f"Refusing to replace existing draft: {output}")
        try:
            previous = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Refusing to replace unreadable draft: {output}") from exc
        if not previous or any(row.get("review_status") != "draft" for row in previous):
            raise ValueError(f"Refusing to replace reviewed cases: {output}")
    rows = specs()
    if len({row["id"] for row in rows}) != len(rows) or any(row.get("split", "holdout") != "holdout" for row in rows):
        raise ValueError("Holdout case IDs must be unique and every row must stay in holdout")
    with tempfile.TemporaryDirectory(prefix="wireless-holdout-draft-") as temp:
        data_root = Path(temp).resolve()
        async with Client(create_server(data_root=data_root), read_timeout_seconds=45) as client:
            visible = {tool.name for tool in (await client.list_tools()).tools}
            for row in rows:
                source = row["source_ref"]
                if not source.startswith("repo:") or not (ROOT / source[5:]).is_file():
                    raise RuntimeError(f"{row['id']}: source_ref does not name a repository file")
                if row["kind"] == "ask_clarification":
                    if row["tool"] not in visible:
                        raise RuntimeError(f"{row['id']}: clarification tool is absent")
                    continue
                steps = row["steps"] if row["kind"] == "tool_workflow" else [row]
                prior_results = []
                for index, step in enumerate(steps):
                    if step["tool"] not in visible:
                        raise RuntimeError(f"{row['id']}: step {index} tool is absent")
                    arguments = workflow_arguments(step, prior_results) if row["kind"] == "tool_workflow" else step["arguments"]
                    result = await client.call_tool(step["tool"], arguments)
                    if result.is_error or not isinstance(result.structured_content, dict):
                        raise RuntimeError(f"{row['id']}: step {index} MCP failed: {result.content}")
                    actual = canonical_result(result.structured_content, data_root)
                    step["arguments"] = arguments
                    step["expected"] = actual
                    prior_results.append(actual)
                if row["kind"] == "tool_workflow":
                    for field, spec in row["answer_fields"].items():
                        if not valid_answer_paths(steps[spec["step"]]["expected"], [spec["path"]]):
                            raise RuntimeError(f"{row['id']}: missing answer field {field}")
                elif not valid_answer_paths(row["expected"], row["answer_paths"]):
                    raise RuntimeError(f"{row['id']}: missing answer_paths in {compact(row['expected'])[:700]}")
    for row in rows:
        row.update(split="holdout", scenario_id=f"independent_{row['id']}",
                   origin_type="expert_authored", reviewer="PENDING_BUSINESS_REVIEW",
                   review_status="draft")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(compact(row) for row in rows) + "\n", encoding="utf-8")
    return {"output": str(output), "cases": len(rows),
            "mcp_calls": sum(len(row["steps"]) if row["kind"] == "tool_workflow" else row["kind"] == "tool_call"
                             for row in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(build(args.output.resolve(), overwrite=args.overwrite)),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
