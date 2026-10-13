"""Serializable MATLAB blePacketDecodeStatus enumeration (R2026a)."""
from __future__ import annotations

from _bluetooth_common import InputError, run_cli


NAMES = {
    0: "Success", -1: "CRCFailed", -2: "LLPDULengthMismatch",
    -3: "InvalidLLPeripheralLatency", -4: "InvalidLLConnectionTimeout",
    -5: "InvalidLLWindowSize", -6: "InvalidLLWindowOffset",
    -7: "InvalidLLConnectionInterval", -8: "InvalidLLChannelMap",
    -51: "IncompleteLLAdvertisingChannelPDU", -52: "InvalidLLHopIncrement",
    -53: "InvalidLLAdvertisingDataLength", -54: "InvalidLLScanResponseDataLength",
    -55: "UnsupportedLLAdvertisingPDUType", -101: "IncompleteLLDataChannelPDU",
    -102: "InvalidLLID", -103: "UnsupportedLLOpCode", -104: "InvalidLLErrorCode",
    -105: "InvalidBluetoothVersion", -106: "ExpectedNonZeroPayload",
    -107: "MICNotSupported", -201: "InvalidGAPADLength", -202: "MismatchGAPADLength",
    -203: "UnsupportedGAPADType", -204: "InvalidGAPAdvertisingInterval",
    -205: "InvalidGAPConnectionIntervalRange", -206: "InvalidGAPConnectionIntervalMinimum",
    -207: "InvalidGAPConnectionIntervalMaximum", -301: "InvalidL2CAPConnectionIntervalRange",
    -302: "InvalidL2CAPPeripheralLatency", -303: "InvalidLECredits",
    -304: "L2CAPSegmentationUnsupported", -305: "MismatchL2CAPHeaderLength",
    -306: "IncompleteL2CAPDataFrame", -307: "InvalidL2CAPChannelIdentifier",
    -308: "InvalidL2CAPCommand", -309: "InvalidL2CAPCommandRejectReason",
    -310: "InvalidL2CAPParameterUpdateResult", -311: "InvalidL2CAPConnectionResult",
    -312: "IllegalL2CAPSignalIdentifier", -313: "InvalidL2CAPConnectionIntervalMinimum",
    -314: "InvalidL2CAPConnectionIntervalMaximum", -315: "InvalidL2CAPConnectionTimeout",
    -316: "InvalidLEPSM", -317: "InvalidL2CAPChannelMTU",
    -318: "InvalidL2CAPChannelMPS", -319: "InvalidL2CAPSDULength",
    -320: "MismatchL2CAPSignalFrameLength", -321: "IncompleteL2CAPSignalFrame",
    -401: "UnsupportedATTOpcode", -402: "IncompleteATTPDU",
    -403: "InvalidATTReqOpcodeInErrorResp", -404: "InvalidATTErrorCode",
    -405: "InvalidATTRxMTU", -406: "InvalidAttributeHandleRange",
    -407: "InvalidAttributeType", -408: "InvalidATTExecuteWriteFlag",
    -409: "MismatchAttributeDataLength", -410: "InvalidATTDataFormat",
}
CODES = {name: code for code, name in NAMES.items()}


def resolve(value) -> dict:
    if isinstance(value, bool):
        raise InputError("status must be a name or integer code")
    if isinstance(value, int):
        name = NAMES.get(value)
        if name is None:
            raise InputError(f"unknown status code: {value}")
        code = value
    elif isinstance(value, str):
        if value not in CODES:
            raise InputError(f"unknown status name: {value}")
        name, code = value, CODES[value]
    else:
        raise InputError("status must be a name or integer code")
    return {"name": name, "code": code, "success": code == 0}


def _handler(_args, request):
    operation = request.get("operation", "lookup")
    if operation == "list":
        return {"result": {"statuses": [resolve(code) for code in sorted(NAMES, reverse=True)],
                           "count": len(NAMES)}}
    if operation == "lookup":
        return {"result": resolve(request.get("status"))}
    if operation == "compare":
        left, right = resolve(request.get("left")), resolve(request.get("right"))
        return {"result": {"equal": left["code"] == right["code"], "left": left, "right": right}}
    raise InputError("operation must be list, lookup, or compare")


if __name__ == "__main__":
    run_cli("ble_packet_decode_status", _handler, description=__doc__)
