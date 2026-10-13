"""Decode Bluetooth Classic BR/EDR packets and validate HEC/CRC."""
from __future__ import annotations

import numpy as np
from scipy.signal import upfirdn
from pathlib import Path
from zipfile import BadZipFile

from _bluetooth_algorithms import whiten
from _bluetooth_common import InputError, complex_from_json, run_cli
from bluetooth_classic_config import create
from bluetooth_classic_waveform import OVERLAY, EDR_GRAY, _bits, _crc, _rrc_coefficients


TYPE_CODES = {0:"NULL",1:"POLL",2:"FHS",3:"DM1",4:"DH1",5:"HV1",6:"HV2",
              7:"HV3",8:"DV",9:"AUX1",10:"DM3",11:"DH3",12:"EV4",13:"EV5",14:"DM5",15:"DH5"}
FEC23 = {"FHS","DM1","DM3","DM5","HV2","EV4","DV"}
CRC_TYPES = {"FHS","DM1","DH1","DM3","DH3","DM5","DH5","EV3","EV4","EV5","DV"}
FIXED_LENGTH = {"ID":0,"NULL":0,"POLL":0,"FHS":18,"HV1":10,"HV2":20,"HV3":30}
ONE_HEADER = {"DM1","DH1","AUX1","DV"}
TWO_HEADER = {"DM3","DH3","DM5","DH5"}
EDR_TYPE_CODES = {
    4:"2-DH1",6:"2-EV3",7:"3-EV3",8:"3-DH1",10:"2-DH3",
    11:"3-DH3",12:"2-EV5",13:"3-EV5",14:"2-DH5",15:"3-DH5",
}


def _number(bits) -> int:
    out=0
    for index,bit in enumerate(bits): out|=int(bit)<<index
    return out


def _decode_lap(access: np.ndarray) -> np.ndarray:
    codeword=access[4:68]^OVERLAY
    message=codeword[::-1][:30]
    info=message[::-1]^OVERLAY[34:64]
    return info[:24]


def _strip_fec(bits: np.ndarray, kind: str) -> np.ndarray:
    if kind=="HV1":
        triples=bits[:bits.size//3*3].reshape(-1,3)
        return (triples.sum(axis=1)>=2).astype(np.uint8)
    if kind not in FEC23:
        return bits
    if kind=="DV":
        return np.concatenate((bits[:80],_strip_fec(bits[80:],"DM1")))
    blocks=bits[:bits.size//15*15].reshape(-1,15)
    return blocks[:,:10].reshape(-1)


def _edr_demodulate(waveform: np.ndarray, mode: str, sps: int) -> np.ndarray:
    order = 4 if mode == "EDR2M" else 8
    width = 2 if order == 4 else 3
    pulse = _rrc_coefficients(sps)
    filtered = upfirdn(pulse, waveform, down=sps)[10:]
    prior = np.concatenate((np.asarray([1+0j]), filtered[:-1]))
    angle = np.angle(filtered * np.conj(prior))
    angle -= np.pi / 4 if order == 4 else 0
    gray_phase = np.mod(np.rint(angle * order / (2 * np.pi)).astype(int), order)
    inverse_gray = np.argsort(EDR_GRAY[order])
    symbols = inverse_gray[gray_phase]
    shifts = np.arange(width-1,-1,-1)
    return ((symbols[:,None] >> shifts) & 1).astype(np.uint8).reshape(-1)[11*width:]


def receive(waveform, properties: dict | None = None) -> dict:
    cfg=create("phy",properties or {})
    if cfg["mode"] not in {"BR", "EDR2M", "EDR3M"}:
        raise InputError("receiver mode must be BR, EDR2M, or EDR3M")
    sps=cfg["samples_per_symbol"]
    data=np.asarray(waveform,dtype=complex).reshape(-1)
    if data.size<625*sps or data.size%sps:
        raise InputError("waveform must contain at least one full 625-symbol slot")
    symbols=data.reshape(-1,sps)
    if sps<2: raise InputError("samples_per_symbol must be at least 2")
    bits=(np.angle(symbols[:,1:]*np.conj(symbols[:,:-1])).mean(axis=1)>=0).astype(np.uint8)
    access_len=68 if cfg["is_id_packet"] else 72
    access=bits[:access_len]
    lap=_decode_lap(access)
    info={"lap":lap.tolist(),"packet_type":"ID" if cfg["is_id_packet"] else "",
          "logical_transport_address":[0,0,0],"header_control_bits":[0,0,0],
          "payload_length":0,"llid":[0,0],"flow_indicator":False}
    if cfg["is_id_packet"]:
        return {"bits":[],"decoded_info":info,"packet_valid":True,"decoded_crc":[0]*16}
    head_coded=bits[access_len:access_len+54]
    head=(head_coded.reshape(18,3).sum(axis=1)>=2).astype(np.uint8)
    state=None
    if cfg["whiten_status"]=="On":
        head,state=whiten(head,0,cfg["whiten_initialization"])
    address=_bits(int(cfg["device_address"],16),48)[::-1]
    uap=address[24:32]
    hec_valid=np.array_equal(head[10:18],_crc(head[:10],0xA7,8,uap[::-1]))
    if not hec_valid:
        return {"bits":[],"decoded_info":info,"packet_valid":False,"decoded_crc":[0]*16}
    info["logical_transport_address"]=head[:3][::-1].tolist()
    code=_number(head[3:7])
    if cfg["mode"] == "BR":
        kind=TYPE_CODES[code]
        if code==7 and cfg["has_extended_sco"]: kind="EV3"
    else:
        kind=EDR_TYPE_CODES.get(code,TYPE_CODES[code])
    info["packet_type"]=kind
    info["header_control_bits"]=head[7:10].tolist()
    if kind in ("NULL","POLL"):
        return {"bits":[],"decoded_info":info,"packet_valid":True,"decoded_crc":[0]*16}
    base_kind=kind[2:] if kind.startswith(("2-","3-")) else kind
    if cfg["mode"] == "BR":
        payload_coded=bits[access_len+54:]
    else:
        offset=(access_len+54+5)*sps
        payload_coded=_edr_demodulate(data[offset:],cfg["mode"],sps)
    payload=_strip_fec(payload_coded,base_kind)
    if cfg["whiten_status"]=="On":
        payload,_=whiten(payload,0,state)
    header_len=(16 if base_kind=="DH1" and cfg["mode"]!="BR" else
                8 if base_kind in ONE_HEADER else 16 if base_kind in TWO_HEADER else 0)
    if base_kind=="DV":
        payload_head=payload[80:88]
    else:
        payload_head=payload[:header_len]
    if header_len:
        info["llid"]=payload_head[:2][::-1].tolist()
        info["flow_indicator"]=bool(payload_head[2])
        length_bits=5 if header_len==8 else 10
        length=_number(payload_head[3:3+length_bits])
    elif base_kind in ("EV3","EV4","EV5"):
        length=cfg["extended_sco_payload_length"]
    else:
        length=FIXED_LENGTH[base_kind]
    info["payload_length"]=length
    if base_kind=="DV":
        body=np.concatenate((payload[:80],payload[88:88+(length*8-80)]))
        crc_input=payload[80:80+8+(length*8-80)]
        received_crc=payload[80+8+(length*8-80):80+8+(length*8-80)+16]
    else:
        body=payload[header_len:header_len+length*8]
        crc_input=payload[:header_len+length*8]
        received_crc=payload[header_len+length*8:header_len+length*8+16]
    if base_kind in CRC_TYPES:
        init=np.concatenate((uap,np.zeros(8,dtype=np.uint8)))[::-1]
        valid=received_crc.size==16 and np.array_equal(received_crc,_crc(crc_input,0x1021,16,init))
        crc_result=received_crc.tolist() if received_crc.size==16 else [0]*16
    else:
        valid=True
        crc_result=[0]*16
    return {"bits":body.tolist(),"decoded_info":info,"packet_valid":bool(valid),
            "decoded_crc":crc_result}


def _handler(_args,request):
    has_inline="waveform" in request
    has_file="waveform_file" in request
    if has_inline == has_file:
        raise InputError("provide exactly one of waveform or waveform_file")
    if has_file:
        raw=request["waveform_file"]
        if not isinstance(raw,str) or not raw:
            raise InputError("waveform_file must be a nonempty .npz path")
        path=Path(raw).expanduser().resolve()
        if path.suffix.lower()!=".npz" or not path.is_file():
            raise InputError("waveform_file must be an existing .npz file")
        try:
            with np.load(path,allow_pickle=False) as archive:
                if "waveform" not in archive.files:
                    raise InputError("waveform_file has no waveform array")
                waveform=np.asarray(archive["waveform"])
        except (OSError,ValueError,BadZipFile) as exc:
            raise InputError(f"cannot load waveform_file: {exc}") from exc
        if waveform.ndim!=1 or not np.iscomplexobj(waveform):
            raise InputError("waveform_file waveform must be a 1-D complex array")
    else:
        waveform=complex_from_json(request["waveform"],"waveform")
    return {"result":receive(waveform,request.get("properties"))}


if __name__=="__main__":
    run_cli("bluetooth_classic_receiver",_handler,description=__doc__)
