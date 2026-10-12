"""Generate Bluetooth Classic BR/EDR baseband packets."""
from __future__ import annotations

import numpy as np
from scipy.signal import upfirdn

from _bluetooth_algorithms import ble_gmsk_modulate, whiten
from _bluetooth_common import InputError, array_result, bit_vector, run_cli
from bluetooth_classic_config import create


OVERLAY = np.asarray([
    0,0,1,1,1,1,1,1,0,0,1,0,1,0,1,0,0,0,1,1,0,0,1,1,1,1,0,1,1,1,0,1,
    0,1,1,0,1,0,0,1,1,0,1,1,0,0,0,1,0,0,1,0,0,0,0,1,1,1,0,0,0,0,0,1], dtype=np.uint8)
BCH64 = np.asarray([1,0,0,1,0,1,0,1,1,0,1,1,1,1,0,0,1,0,0,0,1,1,1,0,1,0,1,0,0,0,0,1,1,0,1],dtype=np.uint8)
BCH15 = np.asarray([1,0,1,0,1,1],dtype=np.uint8)
PACKET_CODES = {"NULL": [0,0,0,0], "POLL": [0,0,0,1], "FHS": [0,0,1,0],
                "DM1": [0,0,1,1], "DH1": [0,1,0,0], "HV1": [0,1,0,1],
                "HV2": [0,1,1,0], "HV3": [0,1,1,1], "DV": [1,0,0,0],
                "AUX1": [1,0,0,1], "DM3": [1,0,1,0], "DH3": [1,0,1,1],
                "EV3": [0,1,1,1], "EV4": [1,1,0,0], "EV5": [1,1,0,1],
                "DM5": [1,1,1,0], "DH5": [1,1,1,1]}
FEC23 = {"DM1", "DM3", "DM5", "HV2", "EV4", "FHS", "DV"}
CRC_TYPES = {"FHS", "DM1", "DH1", "DM3", "DH3", "DM5", "DH5", "EV3", "EV4", "EV5"}
ONE_HEADER = {"DM1", "DH1", "AUX1", "DV"}
TWO_HEADER = {"DM3", "DH3", "DM5", "DH5"}
ONE_SLOT = {"ID", "NULL", "POLL", "FHS", "HV1", "HV2", "HV3", "DV", "EV3", "DM1", "DH1", "AUX1"}
THREE_SLOT = {"EV4", "EV5", "DM3", "DH3"}
EDR_SYNC = {
    "EDR2M": np.asarray([0,0,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1], dtype=np.uint8),
    "EDR3M": np.asarray([0,0,0,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,0,1,0,0,1,0,0,1,0], dtype=np.uint8),
}
EDR_GRAY = {4: np.asarray([0,1,3,2]), 8: np.asarray([0,1,3,2,7,6,4,5])}


def _bits(number: int, width: int) -> np.ndarray:
    return np.asarray([(number >> shift) & 1 for shift in range(width - 1, -1, -1)],dtype=np.uint8)


def _crc(message: np.ndarray, poly: int, width: int, init_bits: np.ndarray) -> np.ndarray:
    register = int("".join(map(str, init_bits.tolist())), 2)
    mask = (1 << width) - 1
    for bit in message:
        feedback = ((register >> (width - 1)) & 1) ^ int(bit)
        register = (register << 1) & mask
        if feedback:
            register ^= poly
    return _bits(register, width)


def _bch(message: np.ndarray, poly: np.ndarray) -> np.ndarray:
    state = [0] * (len(poly) - 1)
    for bit in message:
        feedback = int(bit) ^ state[-1]
        for index in range(len(state) - 1, 0, -1):
            state[index] = state[index - 1] ^ (feedback & int(poly[index]))
        state[0] = feedback
    return np.concatenate((message, np.asarray(state[::-1], dtype=np.uint8)))


def access_code(lap_bits: np.ndarray, is_id: bool) -> np.ndarray:
    information = np.concatenate((lap_bits, lap_bits[-1] ^ np.asarray([0,0,1,1,0,1],dtype=np.uint8)))
    coded = _bch((information ^ OVERLAY[34:64])[::-1], BCH64)[::-1]
    sync = coded ^ OVERLAY
    preamble = sync[0] ^ np.asarray([0,1,0,1],dtype=np.uint8)
    trailer = np.empty(0,dtype=np.uint8) if is_id else sync[-1] ^ np.asarray([1,0,1,0],dtype=np.uint8)
    return np.concatenate((preamble,sync,trailer))


def _payload_header(kind: str, cfg: dict, payload_length: int) -> np.ndarray:
    if kind in ONE_HEADER and not (kind == "DH1" and cfg["mode"] != "BR"):
        return np.concatenate((np.asarray(cfg["llid"][::-1],dtype=np.uint8),
                               np.asarray([int(cfg["flow_indicator"])],dtype=np.uint8),
                               _bits(payload_length,5)[::-1]))
    if kind in TWO_HEADER or (kind == "DH1" and cfg["mode"] != "BR"):
        return np.concatenate((np.asarray(cfg["llid"][::-1],dtype=np.uint8),
                               np.asarray([int(cfg["flow_indicator"])],dtype=np.uint8),
                               _bits(payload_length,10)[::-1],np.zeros(3,dtype=np.uint8)))
    return np.empty(0,dtype=np.uint8)


def _rrc_coefficients(samples_per_symbol: int) -> np.ndarray:
    rolloff, span = 0.4, 20
    time = np.arange(-span * samples_per_symbol / 2,
                     span * samples_per_symbol / 2 + 1) / samples_per_symbol
    with np.errstate(divide="ignore", invalid="ignore"):
        response = (np.sin(np.pi * time * (1 - rolloff))
                    + 4 * rolloff * time * np.cos(np.pi * time * (1 + rolloff))) / (
                    np.pi * time * (1 - (4 * rolloff * time) ** 2))
    response[np.isclose(time, 0)] = 1 + rolloff * (4 / np.pi - 1)
    response[np.isclose(np.abs(time), 1 / (4 * rolloff))] = (
        rolloff / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * rolloff))
                                 + (1 - 2 / np.pi) * np.cos(np.pi / (4 * rolloff))))
    return response / np.sqrt(np.sum(response ** 2))


def _edr_payload_waveform(bits: np.ndarray, mode: str, samples_per_symbol: int) -> np.ndarray:
    order = 4 if mode == "EDR2M" else 8
    width = 2 if order == 4 else 3
    padded = np.pad(bits, (0, -len(bits) % width))
    weights = 1 << np.arange(width - 1, -1, -1)
    indices = padded.reshape(-1, width) @ weights
    phase_steps = (2 * np.pi * EDR_GRAY[order][indices] / order
                   + (np.pi / 4 if order == 4 else 0))
    symbols = np.exp(1j * np.cumsum(phase_steps))
    pulse = _rrc_coefficients(samples_per_symbol)
    span = 20
    filtered = upfirdn(pulse, np.pad(symbols, (0, span)), up=samples_per_symbol)
    start = span * samples_per_symbol // 2
    filtered = filtered[start:start + symbols.size * samples_per_symbol]
    return filtered / np.sqrt(np.var(filtered, ddof=1))


def _fec(message: np.ndarray, kind: str) -> np.ndarray:
    if kind == "HV1":
        return np.repeat(message,3)
    if kind not in FEC23:
        return message
    pad = (-len(message)) % 10
    full = np.pad(message,(0,pad))
    return np.concatenate([_bch(chunk,BCH15) for chunk in full.reshape(-1,10)])


def generate(message: np.ndarray, properties: dict) -> tuple[np.ndarray, dict]:
    cfg = create("waveform", properties)
    mode = cfg["mode"]
    if mode not in {"BR", "EDR2M", "EDR3M"}:
        raise InputError("mode must be BR, EDR2M, or EDR3M")
    raw_kind = cfg["packet_type"]
    if raw_kind.startswith(("2-", "3-")):
        if mode != f"EDR{raw_kind[0]}M":
            raise InputError("EDR-prefixed packet type does not match mode")
        kind = raw_kind[2:]
    else:
        kind = raw_kind
    if mode != "BR" and kind not in {"ID", "NULL", "POLL", "FHS", "DM1", "AUX1", "DH1", "DH3", "DH5", "EV3", "EV5"}:
        raise InputError("unsupported EDR packet_type")
    if kind not in PACKET_CODES and kind != "ID":
        raise InputError("unsupported packet_type")
    # Classic PHY passes msbfirst=false to MATLAB int2bit: LAP and UAP
    # are taken from the least-significant end of the 48-bit address.
    address = _bits(int(cfg["device_address"],16),48)[::-1]
    lap, uap = address[:24], address[24:32]
    payload_length = {"ID":0,"NULL":0,"POLL":0,"FHS":18,"HV1":10,"HV2":20,"HV3":30}.get(kind,cfg["payload_length"])
    payload = bit_vector(message.tolist() if isinstance(message,np.ndarray) else message,"message")
    if kind in {"ID","NULL","POLL"}:
        payload = np.empty(0,dtype=np.uint8)
    elif payload.size != payload_length * 8:
        raise InputError(f"message must contain {payload_length * 8} bits for {kind}")
    access = access_code(lap, kind=="ID")
    if kind == "ID":
        header = np.empty(0,dtype=np.uint8)
    else:
        packet_code = PACKET_CODES[kind]
        if mode == "EDR3M" and kind in {"DH1", "DH3", "DH5"}:
            packet_code = {"DH1": [1,0,0,0], "DH3": [1,0,1,1], "DH5": [1,1,1,1]}[kind]
        elif mode == "EDR2M" and kind in {"DH3", "DH5", "EV3", "EV5"}:
            packet_code = {"DH3": [1,0,1,0], "DH5": [1,1,1,0],
                           "EV3": [0,1,1,0], "EV5": [1,1,0,0]}[kind]
        elif mode == "EDR3M" and kind == "EV3":
            packet_code = [0,1,1,1]
        head = np.concatenate((np.asarray(cfg["logical_transport_address"][::-1],dtype=np.uint8),
                               np.asarray(packet_code[::-1],dtype=np.uint8),
                               np.asarray(cfg["header_control_bits"],dtype=np.uint8)))
        header = _crc(head,0xA7,8,uap[::-1])
        header = np.concatenate((head,header))
    payload_header = _payload_header(kind,cfg,payload_length)
    if kind == "DV":
        if payload.size < 80:
            raise InputError("DV requires at least 80 voice bits")
        crc_body = np.concatenate((payload_header,payload[80:]))
        crc = _crc(crc_body,0x1021,16,np.concatenate((uap,np.zeros(8,dtype=np.uint8)))[::-1])
        data = np.concatenate((payload[:80],crc_body,crc))
    else:
        data = np.concatenate((payload_header,payload))
        if kind in CRC_TYPES:
            data = np.concatenate((data,_crc(data,0x1021,16,np.concatenate((uap,np.zeros(8,dtype=np.uint8)))[::-1])))
    if cfg["whiten_status"] == "On" and kind != "ID":
        whitening, _ = whiten(np.concatenate((header,data)),0,cfg["whiten_initialization"])
        header, data = whitening[:header.size], whitening[header.size:]
    header_fec = np.repeat(header,3)
    data_fec = (np.concatenate((data[:80],_fec(data[80:],"DM1"))) if kind == "DV"
                else _fec(data,kind))
    packet_bits = np.concatenate((access,header_fec,data_fec))
    if mode == "BR":
        modulated = ble_gmsk_modulate(packet_bits,cfg["samples_per_symbol"],cfg["modulation_index"],1)
    else:
        ah = ble_gmsk_modulate(np.concatenate((access,header_fec)),
                               cfg["samples_per_symbol"],cfg["modulation_index"],1)
        if kind in {"ID", "NULL", "POLL"}:
            modulated = ah
        else:
            edr_bits = np.concatenate((EDR_SYNC[mode], data_fec,
                                       np.zeros(4 if mode == "EDR2M" else 6,dtype=np.uint8)))
            psk = _edr_payload_waveform(edr_bits,mode,cfg["samples_per_symbol"])
            modulated = np.concatenate((ah,np.zeros(5*cfg["samples_per_symbol"],dtype=complex),psk))
    slots = 1 if kind in ONE_SLOT else 3 if kind in THREE_SLOT else 5
    target = slots*625*cfg["samples_per_symbol"]
    if modulated.size > target:
        raise InputError("packet exceeds its Bluetooth slot allocation")
    waveform = np.pad(modulated,(0,target-modulated.size))
    return waveform,{"packet_bits":int(packet_bits.size),"access_code_bits":access.tolist(),
                     "payload_length":payload_length,"slots":slots,"mode":mode}


def _handler(args,request):
    properties=request.get("properties",{})
    if not isinstance(properties,dict): raise InputError("properties must be an object")
    message=bit_vector(request.get("message",[]),"message")
    waveform,detail=generate(message,properties)
    result,artifacts=array_result("waveform",waveform,args)
    result.update(detail)
    return {"result":result,"artifacts":artifacts}


if __name__=="__main__":
    run_cli("bluetooth_classic_waveform",_handler,artifacts=True,description=__doc__)
