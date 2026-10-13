"""Encode or write Bluetooth LE packets as PCAP or PCAPNG captures."""
from __future__ import annotations

from pathlib import Path
import struct

from _bluetooth_common import InputError, run_cli
from ble_l2cap import _hex_bytes


def build_pcap(packets: list[dict], *, byte_order="little-endian", phy_header_present=False) -> bytes:
    if byte_order not in {"little-endian", "big-endian"}:
        raise InputError("byte_order must be little-endian or big-endian")
    if not isinstance(phy_header_present, bool):
        raise InputError("phy_header_present must be boolean")
    if not isinstance(packets, list) or not packets:
        raise InputError("packets must be a nonempty list")
    fmt = "<" if byte_order == "little-endian" else ">"
    link_type = 256 if phy_header_present else 251
    out = bytearray(struct.pack(fmt + "IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 0, link_type))
    for packet in packets:
        if not isinstance(packet, dict):
            raise InputError("each packet must be an object")
        unknown = set(packet) - {"packet", "timestamp_us", "phy_header"}
        if unknown:
            raise InputError("unsupported packet fields: " + ", ".join(sorted(unknown)))
        data = _hex_bytes(packet.get("packet"), "packet")
        if phy_header_present:
            header = _hex_bytes(packet.get("phy_header"), "phy_header", length=10)
            data = header + data
        elif "phy_header" in packet:
            raise InputError("phy_header requires phy_header_present=true")
        stamp = packet.get("timestamp_us")
        if not isinstance(stamp, int) or isinstance(stamp, bool) or not 0 <= stamp <= 0xFFFFFFFF * 1_000_000 + 999_999:
            raise InputError("timestamp_us must be a nonnegative integer within PCAP range")
        seconds, microseconds = divmod(stamp, 1_000_000)
        out.extend(struct.pack(fmt + "IIII", seconds, microseconds, len(data), len(data)))
        out.extend(data)
    return bytes(out)


def _pad(data: bytes) -> bytes:
    return data + b"\0" * (-len(data) % 4)


def _option(fmt: str, code: int, value: bytes) -> bytes:
    if len(value) > 65535:
        raise InputError("PCAPNG option exceeds 65535 bytes")
    return struct.pack(fmt + "HH", code, len(value)) + _pad(value)


def _block(fmt: str, kind: int, body: bytes) -> bytes:
    length = len(body) + 12
    if length > 0xFFFFFFFF:
        raise InputError("PCAPNG block exceeds 32-bit size")
    header = struct.pack(fmt + "II", kind, length)
    return header + body + struct.pack(fmt + "I", length)


def build_pcapng(packets: list[dict], *, byte_order="little-endian",
                 phy_header_present=False, file_comment="", interface="BLE") -> bytes:
    """Build MATLAB-compatible SHB, IDB and enhanced packet blocks."""
    if byte_order not in {"little-endian", "big-endian"}:
        raise InputError("byte_order must be little-endian or big-endian")
    if not isinstance(phy_header_present, bool):
        raise InputError("phy_header_present must be boolean")
    if not isinstance(packets, list) or not packets:
        raise InputError("packets must be a nonempty list")
    if not isinstance(file_comment, str) or not isinstance(interface, str) or not interface:
        raise InputError("file_comment and interface must be text; interface cannot be empty")
    fmt = "<" if byte_order == "little-endian" else ">"
    end_options = b"\0\0\0\0"
    shb_body = struct.pack(fmt + "IHHQ", 0x1A2B3C4D, 1, 0, 0xFFFFFFFFFFFFFFFF)
    if file_comment:
        shb_body += _option(fmt, 1, file_comment.encode("utf-8"))
    shb_body += _option(fmt, 4, b"MATLAB") + end_options
    out = bytearray(_block(fmt, 0x0A0D0D0A, shb_body))
    idb_body = struct.pack(fmt + "HHI", 256 if phy_header_present else 251, 0, 0)
    idb_body += _option(fmt, 2, interface.encode("utf-8")) + end_options
    out.extend(_block(fmt, 1, idb_body))
    for packet in packets:
        if not isinstance(packet, dict):
            raise InputError("each packet must be an object")
        unknown = set(packet) - {"packet", "timestamp_us", "phy_header", "packet_comment"}
        if unknown:
            raise InputError("unsupported packet fields: " + ", ".join(sorted(unknown)))
        data = _hex_bytes(packet.get("packet"), "packet")
        if phy_header_present:
            data = _hex_bytes(packet.get("phy_header"), "phy_header", length=10) + data
        elif "phy_header" in packet:
            raise InputError("phy_header requires phy_header_present=true")
        stamp = packet.get("timestamp_us")
        if not isinstance(stamp, int) or isinstance(stamp, bool) or not 0 <= stamp <= 0xFFFFFFFFFFFFFFFF:
            raise InputError("timestamp_us must be a nonnegative 64-bit integer")
        comment = packet.get("packet_comment", "")
        if not isinstance(comment, str):
            raise InputError("packet_comment must be text")
        body = struct.pack(fmt + "IIIII", 0, stamp >> 32, stamp & 0xFFFFFFFF,
                           len(data), len(data)) + _pad(data)
        if comment:
            body += _option(fmt, 1, comment.encode("utf-8")) + end_options
        out.extend(_block(fmt, 6, body))
    return bytes(out)


def _handler(_args, request):
    extension = request.get("file_extension", "pcap")
    if extension not in {"pcap", "pcapng"}:
        raise InputError("file_extension must be pcap or pcapng")
    kwargs = {"byte_order": request.get("byte_order", "little-endian"),
              "phy_header_present": request.get("phy_header_present", False)}
    if extension == "pcapng":
        capture = build_pcapng(request.get("packets"), **kwargs,
                               file_comment=request.get("file_comment", ""),
                               interface=request.get("interface", "BLE"))
    else:
        if "file_comment" in request or "interface" in request:
            raise InputError("file_comment and interface require file_extension=pcapng")
        capture = build_pcap(request.get("packets"), **kwargs)
    result = {f"{extension}_hex": capture.hex().upper(), "bytes": len(capture),
              "packet_count": len(request["packets"])}
    artifacts = []
    if "output_path" in request:
        raw = request["output_path"]
        if not isinstance(raw, str) or not raw:
            raise InputError("output_path must be a nonempty string")
        destination = Path(raw).resolve()
        if destination.suffix.lower() != "." + extension:
            raise InputError(f"output_path must have .{extension} extension")
        if not destination.parent.is_dir():
            raise InputError("output_path parent directory does not exist")
        try:
            with destination.open("xb") as handle:
                handle.write(capture)
        except FileExistsError as exc:
            raise InputError("output_path already exists; files are never overwritten") from exc
        result["output_path"] = str(destination)
        artifacts.append({"path": str(destination), "kind": extension})
    return {"result": result, "artifacts": artifacts}


if __name__ == "__main__":
    run_cli("ble_pcap_writer", _handler, description=__doc__)
