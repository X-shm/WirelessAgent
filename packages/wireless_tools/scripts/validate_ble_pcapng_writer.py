"""Compare exact BLE PCAPNG bytes with R2026a captures."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_pcap_writer import build_pcapng

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "ble_pcapng_writer_samples.json").read_text(encoding="utf-8"))
for case in cases:
    packets = []
    for item in case["packets"]:
        packet = {"packet": item["packet"], "timestamp_us": int(item["timestamp_us"])}
        if case["phy_header_present"]:
            packet["phy_header"] = item["phy_header"]
        if item["packet_comment"]:
            packet["packet_comment"] = item["packet_comment"]
        packets.append(packet)
    capture = build_pcapng(packets, byte_order=case["byte_order"],
                           phy_header_present=case["phy_header_present"],
                           file_comment=case["file_comment"],
                           interface=case["interface"])
    assert capture.hex().upper() == case["pcapng_hex"], (
        case["byte_order"], capture.hex().upper(), case["pcapng_hex"])
print(f"PASS {len(cases)} BLE PCAPNG golden cases")
