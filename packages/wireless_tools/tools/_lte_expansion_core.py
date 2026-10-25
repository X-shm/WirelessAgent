"""Standalone, explicitly scoped LTE public-entry implementations.

These are useful PHY building blocks, not drop-in replacements for every
MATLAB configuration signature.  Every result identifies the selected model.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from _nr_remaining_common import complex_array, json_ready
from lte_prbs import lte_prbs
from lte_modulation import modulate, demodulate
from lte_modulation import bits_per_symbol
from lte_crc import crc_encode, crc_verify
from lte_convolutional_codec import convolutional_encode, convolutional_decode
from lte_ofdm import lte_ofdm_info, modulate as ofdm_modulate
from lte_scfdma import scfdma_info, scfdma_modulate, scfdma_demodulate
from lte_ul_precode import ul_precode
from lte_resource_grid import resource_grid_size
from lte_code_block import _parameters as code_block_parameters
from lte_nsss import nsss, npss
from lte_nrs import nrs
from lte_npbch_indices import npbch_indices
from lte_npusch_drs_indices import npusch_drs_indices
from lte_npusch_indices import npusch_indices
from lte_mib import mib, sl_mib
from lte_psss import psss, ssss, ssss_indices
from lte_pcfich import pcfich_indices, pcfich_info, pcfich_encode, pcfich_decode
from lte_duplexing import duplexing_info
from lte_pbch_indices import pbch_indices
from lte_nb_downlink_indices import npdsch_indices, npdcch_indices
from lte_psbch_indices import psbch_indices, psbch_drs_indices
from lte_sidelink_channel_indices import sidelink_channel_indices
from lte_srs_info import srs_info
from lte_phich_info import phich_info
from lte_pdcch_info import pdcch_info
from lte_pdcch_interleave import pdcch_interleave
from lte_sci_info import sci_info
from lte_ulsch_interleave import ulsch_interleave
from lte_pusch_codebook import ul_pmi_info, pusch_codebook
from lte_dci_info import dci_info
from lte_broadcast import (bch_encode, bch_decode, pbch_encode, pbch_decode,
                           slbch_encode, slbch_decode)
from lte_rach_info import prach_info, nprach_info
from lte_uci_block_code import encode as uci_encode, decode as uci_decode
from lte_control_indices import control_indices
from lte_sidelink_drs import sidelink_drs
from lte_presets import preset as lte_preset
from lte_reference_signals import reference_signal
from lte_pucch_control_indices import pucch_indices as pucch_control_indices
from lte_pucch_drs import pucch_drs
from lte_ul_control_codes import encode as ul_control_encode, decode as ul_control_decode
from lte_dmrs_reference import dmrs_reference
from lte_epdcch_data_indices import epdcch_indices
from lte_npusch_drs import npusch_drs
from lte_turbo import turbo_encode, turbo_decode
from lte_rate_match_turbo import rate_match, rate_recover
from lte_rate_match_convolutional import (rate_match as rate_match_conv,
                                          rate_match_indices)
from lte_tailbiting_soft import decode_tailbiting

GROUPS = json.loads(Path(__file__).with_name("_lte_expansion_names.json").read_text(encoding="utf-8"))
ALL_NAMES = frozenset(name for names in GROUPS.values() for name in names)


def _bits(value, *, allow_empty=False):
    data = np.asarray(value, dtype=int).reshape(-1)
    if (not allow_empty and data.size == 0) or np.any((data != 0) & (data != 1)):
        raise ValueError("bits must be a binary vector")
    return data


def _iq(value):
    data = complex_array(value)
    if not np.all(np.isfinite(data)):
        raise ValueError("complex data must be finite")
    return data


def _model(name, kind, **data):
    return {"entry": name, "model": kind, **{k: json_ready(v) for k, v in data.items()}}


def _config(name, *, nrb=6, cyclic_prefix="Normal", ports=1, mcs=0,
            fields=None, value=None, minimum=None, maximum=None, vector=None,
            start=0, length=None, progress=0, total=1, **kwargs):
    nrb, ports, mcs = int(nrb), int(ports), int(mcs)
    if not 1 <= nrb <= 110 or ports < 1 or not 0 <= mcs <= 28:
        raise ValueError("nrb, ports, or mcs outside supported range")
    if name == "saLteNscRB":
        return _model(name, "LTE resource-block geometry", subcarriers=12)
    if name == "saVectorDataSource":
        values = [] if vector is None else list(vector)
        end = len(values) if length is None else int(start) + int(length)
        return _model(name, "bounded vector source", data=values[int(start):end],
                      next_offset=min(end, len(values)))
    if name == "saProgressBar":
        if total <= 0:
            raise ValueError("total must be positive")
        return _model(name, "headless progress state", fraction=max(0., min(1., progress / total)))
    if name == "evaluateGUIParameter":
        if value is None:
            raise ValueError("value is required")
        if minimum is not None and value < minimum or maximum is not None and value > maximum:
            raise ValueError("value outside bounds")
        return _model(name, "headless parameter validation", value=value, valid=True)
    if name == "lteWarning":
        return _model(name, "headless warning state", message=kwargs.get("message", ""),
                      enabled=bool(kwargs.get("enabled", True)))
    if name == "saLteParamExpand":
        data = {} if fields is None else dict(fields)
        data.update(kwargs)
        return _model(name, "explicit parameter expansion", parameters=data)
    if name in ("lteMIB", "lteSLMIB"):
        data = {"NFrame": 0, "NDLRB": nrb, "PHICHDuration": "Normal"}
        data.update({} if fields is None else fields)
        return _model(name, "serializable broadcast configuration", fields=data)
    if name in ("lteDLSCHInfo", "lteULSCHInfo"):
        block_length = int(kwargs.get("block_length", 40))
        if block_length < 1 or block_length > 1_000_000:
            raise ValueError("block_length must be 1..1000000")
        segmentation = code_block_parameters(block_length)
        segmentation["Bout"] = (segmentation["Cplus"]*segmentation["Kplus"] +
                                 segmentation["Cminus"]*segmentation["Kminus"])
        return _model(name, "LTE transport-block segmentation geometry",
                      block_length=block_length, segmentation=segmentation)
    if name in ("lteDCIInfo", "lteSCIInfo"):
        values = {} if fields is None else dict(fields)
        sizes = {key: len(_bits(value, allow_empty=True)) for key, value in values.items()}
        return _model(name, "explicit ordered-field payload geometry",
                      bit_length=sum(sizes.values()), field_lengths=sizes)
    if name == "lteDuplexingInfo":
        mode = str(kwargs.get("duplex_mode", "FDD")).upper()
        subframe = int(kwargs.get("nsubframe", 0)) % 10
        tdd = ("DSUUUDSUUU", "DSUUDDSUUD", "DSUDDDSUDD",
               "DSUUUDDDDD", "DSUUDDDDDD", "DSUDDDDDDD",
               "DSUUUDSUUD")
        if mode == "FDD":
            kind = "Downlink+Uplink"
        elif mode == "TDD":
            cfg = int(kwargs.get("tdd_config", 0))
            if not 0 <= cfg < len(tdd):
                raise ValueError("tdd_config must be 0..6")
            kind = {"D": "Downlink", "S": "Special", "U": "Uplink"}[tdd[cfg][subframe]]
        else:
            raise ValueError("duplex_mode must be FDD or TDD")
        return _model(name, "LTE FDD/TDD subframe assignment",
                      subframe=subframe, subframe_type=kind, duplex_mode=mode)
    data = {"NCellID": int(kwargs.get("ncellid", 0)), "NDLRB": nrb,
            "CyclicPrefix": cyclic_prefix, "CellRefP": ports, "MCS": mcs}
    data.update({} if fields is None else fields)
    return _model(name, "serializable LTE configuration subset", fields=data)


def _grid(name, *, nrb=6, cyclic_prefix="Normal", ports=1,
          spacing_khz=15.0, link=None, nb_ref_ports=None, **_):
    if name == "lteNBResourceGrid":
        if float(spacing_khz) not in (3.75, 15.0):
            raise ValueError("NB-IoT spacing must be 3.75 or 15 kHz")
        direction = ("uplink" if float(spacing_khz) == 3.75 else "downlink") if link is None else str(link).lower()
        if direction == "uplink":
            shape = [48 if float(spacing_khz) == 3.75 else 12, 7, 1]
        elif direction == "downlink" and float(spacing_khz) == 15:
            count = int(ports if nb_ref_ports is None else nb_ref_ports)
            if count not in (1, 2):
                raise ValueError("nb_ref_ports must be 1 or 2")
            shape = [12, 14, count]
        else:
            raise ValueError("NB-IoT downlink uses 15 kHz spacing")
    else:
        link = "uplink" if "UL" in name else "downlink"
        shape = resource_grid_size(link, nrb, cyclic_prefix, ports)
    return _model(name, "R2026a zero-filled NB-IoT resource grid" if name == "lteNBResourceGrid"
                  else "zero-filled resource grid", size=shape,
                  grid={"shape": shape, "fill_real": 0.0, "fill_imag": 0.0})


def _indices(name, *, nrb=6, prb_set=None, symbols=None, ports=1,
             cyclic_prefix="Normal", index_base=0, **_):
    nrb, ports = int(nrb), int(ports)
    if not 1 <= nrb <= 110 or not 1 <= ports <= 8 or index_base not in (0, 1):
        raise ValueError("invalid grid size, ports, or index base")
    prbs = [0] if prb_set is None else list(np.asarray(prb_set, dtype=int).reshape(-1))
    if any(p < 0 or p >= nrb for p in prbs):
        raise ValueError("PRB index outside grid")
    nsym = 12 if cyclic_prefix.lower() == "extended" else 14
    if symbols is None:
        if "DRS" in name or "DMRS" in name:
            symbols = [3, 10] if nsym == 14 else [2, 8]
        elif "SSS" in name or "PSS" in name:
            symbols = [5, 6]
        else:
            symbols = list(range(nsym))
    symbols = list(np.asarray(symbols, dtype=int).reshape(-1))
    if any(s < 0 or s >= nsym for s in symbols):
        raise ValueError("OFDM symbol index outside subframe")
    rows = [[12*p+k+index_base, s+index_base, ant+index_base]
            for ant in range(ports) for s in symbols for p in prbs for k in range(12)]
    return _model(name, "explicit PRB and OFDM-symbol allocation",
                  indices=rows, count=len(rows), index_base=index_base,
                  grid_shape=[12*nrb, nsym, ports])


def _sequence(name, *, length=None, cinit=0, ncellid=0, root=25,
              cyclic_shift=0, **_):
    if length is None:
        length = 839 if "PRACH" in name else 24
    length, cinit = int(length), int(cinit)
    if not 1 <= length <= 262144:
        raise ValueError("length must be 1..262144")
    if "PRACH" in name and "Detect" not in name:
        if not 1 <= int(root) < length:
            raise ValueError("PRACH root must be inside sequence length")
        n = np.arange(length)
        sequence = np.exp(-1j*np.pi*int(root)*n*(n+1)/length)
        kind = "explicit Zadoff-Chu root sequence"
    else:
        q = lte_prbs(cinit + int(ncellid), 2*length)
        sequence = ((1-2*q[0::2]) + 1j*(1-2*q[1::2])) / math.sqrt(2)
        if cyclic_shift:
            sequence *= np.exp(2j*np.pi*float(cyclic_shift)*np.arange(length)/length)
        kind = "Gold-sequence QPSK with explicit initialization"
    return _model(name, kind, symbols=sequence, length=length)


def _scrambling(name, *, length=24, cinit=None, ncellid=0, nsubframe=0,
               epdcch_nid=None, window=None, mapping="binary", nslid=0,
               nsaid=0, nxid=0, nsubframe_pssch=0, sidelink_mode="D2D",
               rnti=0, **_):
    ncellid, nsubframe = int(ncellid), int(nsubframe)
    if not 0 <= ncellid <= 503 or not 0 <= nsubframe <= 9:
        raise ValueError("ncellid must be 0..503 and nsubframe 0..9")
    if cinit is None:
        if name in ("ltePDCCHPRBS", "lteEPDCCHPRBS"):
            nid = ncellid if epdcch_nid is None else int(epdcch_nid)
            cinit = nsubframe*512+nid
        elif name == "ltePSBCHPRBS":
            if not 0 <= int(nslid) <= 335:
                raise ValueError("nslid must be 0..335")
            cinit = int(nslid)
        elif name == "ltePSCCHPRBS":
            cinit = 510
        elif name == "ltePSSCHPRBS":
            if str(sidelink_mode).upper() not in ("D2D", "V2X"):
                raise ValueError("sidelink_mode must be D2D or V2X")
            nid = int(nsaid) if str(sidelink_mode).upper() == "D2D" else int(nxid)
            if not 0 <= nid <= (255 if str(sidelink_mode).upper() == "D2D" else 65535):
                raise ValueError("invalid Sidelink scrambling identity")
            if not 0 <= int(nsubframe_pssch) <= 9:
                raise ValueError("nsubframe_pssch must be 0..9")
            cinit = nid*16384+int(nsubframe_pssch)*512+510
        elif name in ("ltePUCCH2PRBS", "ltePUCCH3PRBS"):
            if not 0 <= int(rnti) <= 65535:
                raise ValueError("rnti must be 0..65535")
            cinit = (nsubframe+1)*(2*ncellid+1)*65536+int(rnti)
        elif name in ("ltePCFICHPRBS", "ltePHICHPRBS"):
            cinit = (nsubframe+1)*(2*ncellid+1)*512+ncellid
        else:
            cinit = ncellid if name == "ltePBCHPRBS" else 0
    cinit = int(cinit)
    if window is not None:
        if len(window) != 2:
            raise ValueError("window must be [zero_based_start, count]")
        start, count = map(int, window)
    else:
        start, count = 0, int(length)
    if start < 0 or count < 0 or start+count > 262144:
        raise ValueError("invalid PRBS window")
    mode = str(mapping).lower()
    if mode not in ("binary", "signed"):
        raise ValueError("mapping must be binary or signed")
    sequence = lte_prbs(cinit, start+count)[start:]
    if mode == "signed":
        sequence = 1-2*sequence.astype(int)
    model = ("R2026a LTE physical-channel Gold sequence" if name in
             ("ltePBCHPRBS", "ltePDCCHPRBS", "ltePCFICHPRBS", "ltePHICHPRBS",
              "lteEPDCCHPRBS", "ltePSBCHPRBS", "ltePSCCHPRBS", "ltePSSCHPRBS",
              "ltePUCCH2PRBS", "ltePUCCH3PRBS") else "LTE Gold sequence with explicit cinit")
    return _model(name, model, bits=sequence, length=count, cinit=cinit,
                  mapping=mode)


_CFI_WORDS = {
    1: ([0, 1, 1]*11)[:32],
    2: ([1, 0, 1]*11)[:32],
    3: ([1, 1, 0]*11)[:32],
}


def _control(name, *, bits=None, cfi=1, fields=None, length=None, mask=0,
             code_rate=None, soft_bits=None, **_):
    if name == "lteCFIDecode":
        values = np.asarray(_CFI_WORDS[1] if bits is None and soft_bits is None else
                            bits if soft_bits is None else soft_bits, dtype=float).reshape(-1)
        if values.size == 0 or not np.all(np.isfinite(values)):
            raise ValueError("CFI decoder requires finite soft values")
        distances = {v: float(np.square(values-np.resize(np.asarray(pattern), len(values))).sum())
                     for v, pattern in _CFI_WORDS.items()}
        winner = min(distances, key=distances.get)
        return _model(name, "soft minimum-distance CFI block decoding",
                      cfi=winner, distance=distances[winner])
    raw = _bits([0, 1, 0, 1, 1, 0, 0, 1] if bits is None else bits)
    if name == "lteCFI":
        if int(cfi) not in _CFI_WORDS:
            raise ValueError("cfi must be 1, 2, or 3")
        return _model(name, "3GPP 32-bit CFI block word", coded_bits=_CFI_WORDS[int(cfi)])
    if name.endswith(("Interleave", "Deinterleave")):
        columns = 4
        if len(raw) % columns:
            raise ValueError("four-column permutation requires a multiple of four bits")
        if name.endswith("Deinterleave"):
            out = raw.reshape(columns, -1).T.reshape(-1)
        else:
            out = raw.reshape(-1, columns).T.reshape(-1)
        return _model(name, "four-column reversible bit permutation",
                      bits=out, columns=columns)
    if name in ("lteDCI", "lteSCI", "lteDCIInfo", "lteSCIInfo"):
        packed = raw if fields is None else _bits([b for value in fields.values() for b in value])
        return _model(name, "explicit ordered-field bit packing",
                      bits=packed, bit_length=len(packed), fields=fields or {})
    if name.endswith(("ResourceAllocation", "Space", "Search")):
        return _indices(name, nrb=6)
    if name.endswith("Encode"):
        if name in ("lteDCIEncode", "lteSCIEncode"):
            encoded = convolutional_encode(crc_encode(raw, "16", mask))
            model = "CRC16 plus LTE tail-biting convolutional encoding"
        else:
            count = int(length) if length is not None else max(8, 2*len(raw))
            encoded = np.resize(raw, count)
            model = "explicit repetition-coded control bits"
        return _model(name, model, coded_bits=encoded, coded_length=len(encoded))
    if name.endswith("Decode"):
        if name in ("lteDCIDecode", "lteSCIDecode") and len(raw) >= 18 and len(raw) % 3 == 0:
            decoded, metric = convolutional_decode(raw)
            valid, payload = crc_verify(decoded, "16", mask)
            return _model(name, "hard Viterbi plus CRC16", bits=payload,
                          crc_ok=valid, path_metric=metric)
        if length is None:
            length = max(1, len(raw)//2)
        decoded = np.array([np.mean(raw[i::int(length)]) >= .5 for i in range(int(length))], dtype=int)
        return _model(name, "majority decoding of repetition-coded bits", bits=decoded)
    return _model(name, "explicit control-bit stream", bits=raw)


def _dci_encode(name, *, bits=None, pdcch_format=0, rnti=0,
                length=None, mask=None, **_):
    raw = _bits([0, 1]*16 if bits is None else bits)
    fmt = int(pdcch_format)
    identity = int(rnti if mask is None else mask)
    if not 0 <= fmt <= 3 or not 0 <= identity <= 65535:
        raise ValueError("PDCCH format must be 0..3 and RNTI 0..65535")
    outlen = 72*(2**fmt) if length is None else int(length)
    if outlen < 1:
        raise ValueError("output length must be positive")
    with_crc = crc_encode(raw, "16", identity)
    coded = rate_match_conv(convolutional_encode(with_crc), outlen)
    mcrc = int("".join(map(str, with_crc[-16:])), 2)
    return _model(name, "R2026a LTE DCI CRC16, tail-biting convolutional code and rate matching",
                  coded_bits=coded, coded_length=outlen, mcrc=mcrc)


def _dci_decode(name, *, bits=None, soft_bits=None, payload_length=16,
                rnti=0, mask=None, **_):
    identity = int(rnti if mask is None else mask)
    if not 0 <= identity <= 65535:
        raise ValueError("RNTI must be 0..65535")
    if soft_bits is None:
        if bits is None:
            bits = _dci_encode("lteDCIEncode", bits=[0, 1]*8)["coded_bits"]
        received = 2*_bits(bits).astype(float)-1
    else:
        received = np.asarray(soft_bits, dtype=float).reshape(-1)
    length = int(payload_length)
    if length < 1 or len(received) < 1:
        raise ValueError("payload length and coded input must be nonempty")
    restored = np.zeros(3*(length+16), dtype=float)
    indices = rate_match_indices(len(restored), len(received))
    np.add.at(restored, indices, received)
    decoded, metric = decode_tailbiting(restored)
    payload = decoded[:-16]
    masked_crc = decoded[-16:]
    plain_crc = crc_encode(payload, "16")[-16:]
    recovered_rnti = int("".join(map(str, masked_crc ^ plain_crc)), 2)
    mcrc = int("".join(map(str, masked_crc)), 2)
    return _model(name, "R2026a LTE DCI soft Viterbi decoding and CRC identity recovery",
                  bits=payload, crc_rnti=recovered_rnti, mcrc=mcrc,
                  crc_ok=recovered_rnti == identity, path_metric=metric)


def _sci_encode(name, *, bits=None, nrb=6, sidelink_mode="D2D",
                cyclic_prefix="Normal", length=None, **_):
    mode, cp = str(sidelink_mode).upper(), str(cyclic_prefix).lower()
    if mode not in ("D2D", "V2X") or cp not in ("normal", "extended"):
        raise ValueError("invalid Sidelink mode or cyclic prefix")
    if mode == "V2X" and cp != "normal":
        raise ValueError("V2X SCI requires Normal cyclic prefix")
    default_length = sci_info(nrb)["Format1" if mode == "V2X" else "Format0"]
    raw = _bits([0]*default_length if bits is None else bits)
    output_length = int(length) if length is not None else (480 if mode == "V2X" else
                                                            288 if cp == "normal" else 240)
    coded = _dci_encode("lteDCIEncode", bits=raw, rnti=0,
                        length=output_length)
    matrix_cp = "Extended" if mode == "V2X" else cyclic_prefix
    interleaved = ulsch_interleave(coded["coded_bits"],
                                   cyclic_prefix=matrix_cp, modulation="QPSK")
    return _model(name, "R2026a LTE SCI CRC16, tail-biting code and PUSCH interleaving",
                  coded_bits=interleaved, coded_length=output_length,
                  mcrc=coded["mcrc"])


def _sci_decode(name, *, bits=None, soft_bits=None, payload_length=None,
                nrb=6, sidelink_mode="D2D", cyclic_prefix="Normal", **_):
    mode = str(sidelink_mode).upper()
    if payload_length is None:
        payload_length = sci_info(nrb)["Format1" if mode == "V2X" else "Format0"]
    if soft_bits is None:
        if bits is None:
            bits = _sci_encode("lteSCIEncode", nrb=nrb,
                               sidelink_mode=sidelink_mode,
                               cyclic_prefix=cyclic_prefix)["coded_bits"]
        received = 2*_bits(bits).astype(float)-1
    else:
        received = np.asarray(soft_bits, dtype=float).reshape(-1)
    matrix_cp = "Extended" if mode == "V2X" else cyclic_prefix
    deinterleaved = ulsch_interleave(received, cyclic_prefix=matrix_cp,
                                     modulation="QPSK", inverse=True)
    decoded = _dci_decode("lteDCIDecode", soft_bits=deinterleaved,
                          payload_length=payload_length, rnti=0)
    return _model(name, "R2026a LTE SCI deinterleaving, soft Viterbi and CRC check",
                  bits=decoded["bits"], crc_error=not decoded["crc_ok"],
                  mcrc=decoded["mcrc"])


def _channel(name, *, bits=None, symbols=None, cinit=0, modulation="QPSK",
             length=None, nrb=6, prb_set=None, **_):
    if name.endswith("Decode") or name.endswith("Recover"):
        values = _iq({"real": [1., -1.], "imag": [1., -1.]} if symbols is None else symbols)
        hard = demodulate(values, modulation)
        if length is not None:
            hard = hard[:int(length)]
        sequence = lte_prbs(cinit, len(hard))
        return _model(name, "hard symbol demapping and explicit Gold descrambling",
                      bits=hard ^ sequence, modulation=modulation)
    raw = _bits([0, 1]*12 if bits is None else bits)
    scrambled = raw ^ lte_prbs(cinit, len(raw))
    output = modulate(scrambled, modulation)
    return _model(name, "explicit Gold scrambling and LTE constellation mapping",
                  symbols=output, modulation=modulation, bit_count=len(raw))


def _sidelink_channel(name, *, bits=None, nslid=0, nsaid=0, nxid=0,
                      nsubframe_pssch=0, sidelink_mode="D2D",
                      cyclic_prefix="Normal", modulation="QPSK", **_):
    default_length = 1152 if name == "ltePSBCH" else 288
    raw = _bits([0]*default_length if bits is None else bits)
    if name != "ltePSSCH":
        modulation = "QPSK"
    elif modulation not in ("QPSK", "16QAM"):
        raise ValueError("PSSCH modulation must be QPSK or 16QAM")
    mode, cp = str(sidelink_mode).upper(), str(cyclic_prefix).lower()
    if mode not in ("D2D", "V2X") or cp not in ("normal", "extended"):
        raise ValueError("invalid sidelink mode or cyclic prefix")
    if mode == "V2X" and cp != "normal":
        raise ValueError("V2X sidelink requires Normal cyclic prefix")
    prbs_name = name + "PRBS"
    mask = np.asarray(_scrambling(prbs_name, length=len(raw), nslid=nslid,
                                 nsaid=nsaid, nxid=nxid,
                                 nsubframe_pssch=nsubframe_pssch,
                                 sidelink_mode=mode)["bits"], dtype=int)
    modulated = modulate(raw ^ mask, modulation)
    if name == "ltePSBCH":
        nprb = 6
    elif name == "ltePSCCH":
        nprb = math.ceil(len(modulated)/144)
    else:
        nre = 144 if mode == "D2D" and cp == "normal" else 120
        nprb = math.ceil(len(modulated)/nre)
    if len(modulated) % (12*nprb):
        raise ValueError("codeword length is incompatible with the SC-FDMA PRB allocation")
    symbols = ul_precode(modulated, nprb).reshape(-1)
    return _model(name, "R2026a LTE sidelink scrambling, modulation and DFT precoding",
                  symbols=symbols, modulation=modulation,
                  nprb=nprb, bit_count=len(raw))


def _sidelink_channel_decode(name, *, symbols=None, nslid=0, nsaid=0,
                             nxid=0, nsubframe_pssch=0, sidelink_mode="D2D",
                             cyclic_prefix="Normal", modulation="QPSK", **_):
    base = name.removesuffix("Decode")
    if symbols is None:
        symbols = _sidelink_channel(base, nslid=nslid, nsaid=nsaid, nxid=nxid,
                                    nsubframe_pssch=nsubframe_pssch,
                                    sidelink_mode=sidelink_mode,
                                    cyclic_prefix=cyclic_prefix,
                                    modulation=modulation)["symbols"]
    received = _iq(symbols).reshape(-1)
    if base != "ltePSSCH":
        modulation = "QPSK"
    if base == "ltePSBCH":
        nprb = 6
    elif base == "ltePSCCH":
        nprb = math.ceil(len(received)/144)
    else:
        nre = 144 if str(sidelink_mode).upper() == "D2D" and str(cyclic_prefix).lower() == "normal" else 120
        nprb = math.ceil(len(received)/nre)
    decoded = ul_precode(received, nprb, inverse=True).reshape(-1)
    if modulation == "QPSK":
        soft = np.column_stack((-decoded.real, -decoded.imag)).reshape(-1)
    elif modulation == "16QAM" and base == "ltePSSCH":
        threshold = 2/math.sqrt(10)
        soft = np.column_stack((-decoded.real, -decoded.imag,
                                abs(decoded.real)-threshold,
                                abs(decoded.imag)-threshold)).reshape(-1)
    else:
        raise ValueError("unsupported sidelink modulation")
    if base == "ltePSCCH":
        soft[-24:] = 0
    elif base == "ltePSSCH":
        soft[-12*nprb*bits_per_symbol(modulation):] = 0
    mask = np.asarray(_scrambling(base+"PRBS", length=len(soft),
                                 nslid=nslid, nsaid=nsaid, nxid=nxid,
                                 nsubframe_pssch=nsubframe_pssch,
                                 sidelink_mode=sidelink_mode,
                                 mapping="signed")["bits"], dtype=int)
    soft *= mask
    return _model(name, "R2026a LTE sidelink DFT deprecoding and soft demodulation",
                  soft_bits=soft, symbols=decoded, nprb=nprb)


def _coding(name, *, bits=None, length=None, permutation=None,
            soft_bits=None, iterations=5, rv=0, ncb=None,
            block_size=None, transport_block_length=None, filler_count=0, **_):
    if name == "lteTurboEncode":
        if bits is None:
            raw = np.asarray([0, 1]*20, dtype=int)
        else:
            raw = np.asarray(bits, dtype=int).reshape(-1)
        coded = turbo_encode(raw)
        return _model(name, "TS 36.212 QPP 8-state PCCC with trellis termination",
                      coded_bits=coded, coded_length=len(coded))
    if name == "lteTurboDecode":
        if soft_bits is None:
            if bits is None:
                coded = turbo_encode([0, 1]*20)
                soft_bits = 8*(2*coded.astype(float)-1)
            else:
                soft_bits = bits
        decoded = turbo_decode(soft_bits, iterations)
        return _model(name, "TS 36.212 QPP iterative Max-Log-MAP decoding",
                      bits=decoded, iterations=int(iterations))
    if name == "lteRateMatchTurbo":
        coded = turbo_encode([0, 1]*20) if bits is None else np.asarray(bits, dtype=int).reshape(-1)
        output_length = len(coded) if length is None else int(length)
        matched = rate_match(coded, output_length, rv, ncb)
        return _model(name, "TS 36.212 one-code-block Turbo rate matching",
                      bits=matched, output_length=len(matched), rv=int(rv))
    if name == "lteRateRecoverTurbo":
        if block_size is None:
            block_size = 40 if transport_block_length is None else int(transport_block_length)+24
        if soft_bits is None:
            if bits is None:
                coded = turbo_encode([0, 1]*20)
                matched = rate_match(coded, 80, rv, ncb)
                soft_bits = 2*matched.astype(float)-1
            else:
                soft_bits = bits
        restored = rate_recover(soft_bits, block_size, rv, filler_count, ncb)
        return _model(name, "TS 36.212 one-code-block Turbo soft rate recovery",
                      soft_bits=restored, block_size=int(block_size), rv=int(rv))
    raw = _bits([0, 1]*12 if bits is None else bits)
    return _control(name, bits=raw, length=length)


def _receiver(name, *, received=None, reference=None, waveform=None,
              taps=None, noise_variance=0., **_):
    rx = _iq({"real": [1., 1.], "imag": [0., 0.]} if received is None else received)
    if "FrameOffset" in name or name.endswith("Detect"):
        pilot = _iq({"real": [1.], "imag": [0.]} if reference is None else reference).reshape(-1)
        metric = abs(np.correlate(rx.reshape(-1), pilot, mode="valid"))
        index = int(np.argmax(metric))
        return _model(name, "explicit-reference matched-filter timing",
                      offset=index, peak=float(metric[index]), metric=metric)
    if "PerfectChannelEstimate" in name:
        h = _iq({"real": [1.], "imag": [0.]} if taps is None else taps)
        return _model(name, "explicit channel taps", channel=h, noise_variance=0.)
    pilot = _iq({"real": np.ones(rx.shape).tolist(), "imag": np.zeros(rx.shape).tolist()}
                if reference is None else reference)
    if rx.shape != pilot.shape or np.any(abs(pilot) == 0):
        raise ValueError("received and reference shapes must match; reference must be nonzero")
    h = rx / pilot
    variance = float(np.mean(abs(h-np.mean(h))**2)) if h.size > 1 else 0.
    return _model(name, "explicit-reference least-squares channel estimate",
                  channel=h, noise_variance=variance)


def _precode(name, *, symbols=None, n=1, resource_type="Subcarrier", **_):
    values = _iq({"real": [1.], "imag": [0.]} if symbols is None else symbols)
    inverse = "Deprecode" in name or "Decode" in name
    result = ul_precode(values, n, resource_type, inverse)
    return _model(name, "unitary DFT spreading or despreading", symbols=result)


def _waveform(name, *, waveform=None, grid=None, nrb=6,
              cyclic_prefix="Normal", sample_rate_hz=1.92e6,
              taps=None, seed=0, **_):
    if name in ("lte3DChannel", "lteHSTChannel", "lteMovingChannel"):
        values = _iq({"real": [1., 0., 0.], "imag": [0., 0., 0.]}
                     if waveform is None else waveform).reshape(-1)
        h = _iq({"real": [1.], "imag": [0.]} if taps is None else taps).reshape(-1)
        output = np.convolve(values, h)[:len(values)]
        return _model(name, "explicit tapped FIR channel", waveform=output,
                      sample_rate_hz=sample_rate_hz, taps=h, seed=seed)
    if name == "lteThroughputAnalyzer":
        raise ValueError("use transport_blocks and elapsed_seconds with throughput analyzer")
    if "Generator" in name or name.endswith("Tool"):
        return _config(name, nrb=nrb, cyclic_prefix=cyclic_prefix)
    if name.endswith("SCFDMAInfo"):
        return _model(name, "LTE SC-FDMA parameter calculation",
                      info=scfdma_info(nrb, cyclic_prefix))
    if name.endswith("SCFDMAModulate"):
        if grid is None:
            grid = np.zeros((12*int(nrb), 14 if cyclic_prefix == "Normal" else 12), complex)
        signal, info = scfdma_modulate(_iq(grid), nrb, cyclic_prefix)
        return _model(name, "DFT-spread OFDM subframe", waveform=signal, info=info)
    if name.endswith("SCFDMADemodulate"):
        if waveform is None:
            raise ValueError("waveform is required")
        values, info = scfdma_demodulate(_iq(waveform), nrb, cyclic_prefix)
        return _model(name, "DFT-despread OFDM subframe", grid=values, info=info)
    return _config(name, nrb=nrb, cyclic_prefix=cyclic_prefix)


def execute(name, **params):
    if name not in ALL_NAMES:
        raise ValueError(f"unknown LTE public entry: {name}")
    if name == "lteMIB":
        return _model(name, "R2026a LTE 24-bit MIB encoding and decoding", **mib(**params))
    if name == "lteSLMIB":
        return _model(name, "R2026a LTE sidelink 40-bit MIB encoding and decoding",
                      **sl_mib(**params))
    if name in ("ltePSSS", "ltePSSSIndices"):
        values, positions = psss(**params)
        return _model(name, "R2026a primary sidelink synchronization sequence and RE positions",
                      symbols=values, indices=positions, count=len(values))
    if name == "ltePCFICHIndices":
        positions = pcfich_indices(**params)
        return _model(name, "R2026a LTE PCFICH RE positions",
                      indices=positions, count=len(positions))
    if name == "ltePCFICHInfo":
        return _model(name, "R2026a LTE PCFICH resource geometry",
                      info=pcfich_info())
    if name == "ltePCFICH":
        raw = _bits(params.pop("bits", _CFI_WORDS[1]))
        return _model(name, "R2026a LTE single-port PCFICH processing",
                      symbols=pcfich_encode(raw, **params))
    if name == "ltePCFICHDecode":
        raw = params.pop("symbols", None)
        if raw is None:
            raw = pcfich_encode(_CFI_WORDS[1], **params)
        return _model(name, "R2026a LTE single-port PCFICH soft decoding",
                      soft_bits=pcfich_decode(_iq(raw), **params))
    if name == "lteDuplexingInfo":
        info = duplexing_info(**params)
        return _model(name, "R2026a LTE FDD and TDD SSC-0 subframe geometry",
                      info=info, subframe_type=info["SubframeType"])
    if name == "lteSRSInfo":
        return _model(name, "R2026a LTE cell-specific SRS subframe schedule",
                      info=srs_info(**params))
    if name == "ltePHICHInfo":
        return _model(name, "R2026a LTE FDD PHICH resource geometry",
                      info=phich_info(**params))
    if name == "ltePDCCHInfo":
        return _model(name, "R2026a LTE FDD PDCCH control-region geometry",
                      info=pdcch_info(**params))
    if name in ("ltePDCCHIndices", "ltePHICHIndices"):
        positions = control_indices(name, **params)
        return _model(name, "R2026a LTE baseline FDD control RE allocation",
                      indices=positions, count=len(positions), index_base=params.get("index_base", 0))
    if name in ("lteCSIRS", "lteCSIRSIndices", "ltePRS", "ltePRSIndices"):
        values, positions = reference_signal(name, **params)
        if name.endswith("Indices"):
            return _model(name, "R2026a LTE baseline FDD reference-signal RE positions",
                          indices=positions, count=len(positions),
                          index_base=params.get("index_base", 0))
        return _model(name, "R2026a LTE baseline FDD reference-signal symbols",
                      symbols=values, count=len(values))
    if name in ("lteDMRS", "lteDMRSIndices", "lteEPDCCHDMRS",
                "lteEPDCCHDMRSIndices"):
        values, positions = dmrs_reference(name, **params)
        if name.endswith("Indices"):
            return _model(name, "R2026a LTE baseline DM-RS RE positions",
                          indices=positions, count=len(positions),
                          index_base=params.get("index_base", 0))
        return _model(name, "R2026a LTE baseline DM-RS symbols",
                      symbols=values, count=len(values))
    if name == "lteEPDCCHIndices":
        positions, info = epdcch_indices(**params)
        return _model(name, "R2026a LTE baseline EPDCCH data RE allocation",
                      indices=positions, info=info, count=len(positions),
                      index_base=params.get("index_base", 0))
    if name in ("ltePUCCH1Indices", "ltePUCCH1DRSIndices",
                "ltePUCCH2Indices", "ltePUCCH2DRSIndices",
                "ltePUCCH3Indices", "ltePUCCH3DRSIndices"):
        positions = pucch_control_indices(name, **params)
        return _model(name, "R2026a LTE baseline FDD PUCCH RE allocation",
                      indices=positions, count=len(positions),
                      index_base=params.get("index_base", 0))
    if name in ("ltePUCCH1DRS", "ltePUCCH2DRS", "ltePUCCH3DRS"):
        symbols, info = pucch_drs(name, **params)
        return _model(name, "R2026a LTE baseline FDD PUCCH DRS sequence",
                      symbols=symbols, info=info, count=len(symbols))
    if name == "lteDLSCHInfo":
        length = int(params.get("block_length", 40))
        if not 1 <= length <= 1000000:
            raise ValueError("block_length must be 1..1000000")
        seg = code_block_parameters(length+24)
        info = {"C": seg["C"], "Km": seg["Kminus"],
                "Cm": seg["Cminus"], "Kp": seg["Kplus"],
                "Cp": seg["Cplus"], "F": seg["F"], "L": seg["L"],
                "Bout": seg["Cminus"]*seg["Kminus"] +
                        seg["Cplus"]*seg["Kplus"]}
        return _model(name, "R2026a LTE DL-SCH transport CRC and code-block segmentation",
                      info=info, segmentation=seg)
    if name == "lteSCIInfo":
        return _model(name, "R2026a LTE SCI format 0/1 payload lengths",
                      info=sci_info(params.get("nrb", 6)))
    if name == "ltePRACHInfo":
        return _model(name, "R2026a LTE FDD baseline PRACH geometry",
                      info=prach_info(**params))
    if name == "lteNPRACHInfo":
        return _model(name, "R2026a NB-IoT FDD baseline NPRACH geometry",
                      info=nprach_info(**params))
    if name == "lteDCIInfo":
        if "fields" in params:
            return _config(name, **params)
        return _model(name, "R2026a LTE symmetric-bandwidth DCI format lengths",
                      info=dci_info(params.get("nrb", 6),
                                    params.get("ports", 1),
                                    params.get("duplex_mode", "FDD"),
                                    params.get("n_ul_rb")))
    if name == "lteSLSCFDMAInfo":
        nrb = int(params.get("nrb", 6))
        cp = params.get("cyclic_prefix", "Normal")
        geometry = scfdma_info(nrb, cp)
        info = {"SamplingRate": geometry["samplingrate"],
                "Nfft": geometry["nfft"],
                "Windowing": int(params.get("windowing", geometry["windowing"])),
                "CyclicPrefixLengths": geometry["cplengths"]}
        if info["Windowing"] < 0 or info["Windowing"] % 2:
            raise ValueError("windowing must be a nonnegative even number")
        return _model(name, "R2026a LTE sidelink SC-FDMA sampling and CP geometry",
                      info=info)
    if name == "lteULPMIInfo":
        return _model(name, "R2026a LTE uplink wideband PMI geometry",
                      info=ul_pmi_info(params.get("nrb", 6),
                                       params.get("n_tx_ants", 1),
                                       params.get("n_layers", 1)))
    if name == "lteBCH":
        raw = params.get("bits", [0]*24)
        coded = bch_encode(raw, params.get("cyclic_prefix", "Normal"),
                           params.get("ports", 1), params.get("length"))
        return _model(name, "R2026a LTE BCH CRC mask, convolutional code and rate matching",
                      coded_bits=coded, coded_length=len(coded))
    if name == "lteBCHDecode":
        soft = params.get("soft_bits")
        if soft is None:
            raw = params.get("bits")
            if raw is None:
                raw = bch_encode([0]*24)
            soft = 2*np.asarray(raw, dtype=float)-1
        payload, ports, metric = bch_decode(soft, params.get("transport_length", 24))
        return _model(name, "R2026a LTE BCH soft Viterbi and port CRC recovery",
                      bits=payload, cell_ref_ports=ports,
                      crc_ok=ports != 0, path_metric=metric)
    if name == "ltePBCH":
        raw = params.get("bits")
        if raw is None:
            raw = bch_encode([0]*24, ports=1)
        symbols = pbch_encode(raw, params.get("ncellid", 0))
        return _model(name, "R2026a LTE single-port PBCH scrambling and QPSK",
                      symbols=symbols, count=len(symbols))
    if name == "ltePBCHDecode":
        values = params.get("symbols")
        if values is None:
            values = pbch_encode(bch_encode([0]*24, ports=1),
                                 params.get("ncellid", 0))
        soft, constellation, payload, ports, metric = pbch_decode(
            _iq(values), params.get("ncellid", 0),
            params.get("transport_length", 24))
        return _model(name, "R2026a LTE full-block single-port PBCH decoding",
                      soft_bits=soft, symbols=constellation, trblk=payload,
                      cell_ref_ports=ports, nfmod4=0, path_metric=metric)
    if name == "lteSLBCH":
        coded = slbch_encode(params.get("bits", [0]*40),
                             params.get("sidelink_mode", "D2D"),
                             params.get("cyclic_prefix", "Normal"))
        return _model(name, "R2026a LTE SL-BCH convolutional code and sidelink interleaving",
                      coded_bits=coded, coded_length=len(coded))
    if name == "lteSLBCHDecode":
        soft = params.get("soft_bits")
        if soft is None:
            raw = params.get("bits")
            if raw is None:
                raw = slbch_encode([0]*40, params.get("sidelink_mode", "D2D"),
                                   params.get("cyclic_prefix", "Normal"))
            soft = 2*np.asarray(raw, dtype=float)-1
        payload, error, metric = slbch_decode(
            soft, params.get("sidelink_mode", "D2D"),
            params.get("cyclic_prefix", "Normal"))
        return _model(name, "R2026a LTE SL-BCH soft deinterleaving and CRC recovery",
                      bits=payload, crc_error=error, path_metric=metric)
    if name in ("ltePUSCHPrecode", "ltePUSCHDeprecode"):
        values = _iq(params.get("symbols", {"real": [1.], "imag": [0.]}))
        inverse = name.endswith("Deprecode")
        if inverse and values.ndim == 2:
            antennas = int(params.get("n_tx_ants", values.shape[1]))
        else:
            antennas = int(params.get("n_tx_ants", 1))
        result = pusch_codebook(values, n_tx_ants=antennas,
                                n_layers=params.get("n_layers"),
                                pmi=params.get("pmi", 0), inverse=inverse)
        return _model(name, "R2026a LTE uplink PUSCH codebook matrix processing",
                      symbols=result)
    if name == "lteDCIEncode":
        return _dci_encode(name, **params)
    if name == "lteDCIDecode":
        return _dci_decode(name, **params)
    if name == "lteSCIEncode":
        return _sci_encode(name, **params)
    if name == "lteSCIDecode":
        return _sci_decode(name, **params)
    if name in ("lteULSCHInterleave", "lteULSCHDeinterleave"):
        values = params.get("bits", [0, 1]*12)
        result = ulsch_interleave(values,
                                  cyclic_prefix=params.get("cyclic_prefix", "Normal"),
                                  shortened=params.get("shortened", 0),
                                  modulation=params.get("modulation", "QPSK"),
                                  n_layers=params.get("n_layers", 1),
                                  inverse=name.endswith("Deinterleave"))
        return _model(name, "R2026a LTE data-only UL-SCH matrix interleaving",
                      bits=result)
    if name in ("ltePDCCHInterleave", "ltePDCCHDeinterleave"):
        field = "symbols" if "symbols" in params else "bits"
        values = params.get(field, [0, 1]*18)
        output = pdcch_interleave(values, params.get("ncellid", 0),
                                  inverse=name.endswith("Deinterleave"))
        return _model(name, "R2026a LTE PDCCH REG permutation and cell shift",
                      **{field: output})
    if name in ("ltePSBCH", "ltePSCCH", "ltePSSCH"):
        return _sidelink_channel(name, **params)
    if name in ("ltePSBCHDecode", "ltePSCCHDecode", "ltePSSCHDecode"):
        return _sidelink_channel_decode(name, **params)
    if name == "ltePBCHIndices":
        positions = pbch_indices(**params)
        return _model(name, "R2026a LTE PBCH scheduled RE positions",
                      indices=positions, count=len(positions))
    if name in ("lteNPDSCHIndices", "lteNPDCCHIndices"):
        positions, info = (npdsch_indices(**params) if name == "lteNPDSCHIndices"
                           else npdcch_indices(**params))
        return _model(name, "R2026a NB-IoT downlink channel RE positions",
                      indices=positions, count=len(positions), info=info)
    if name == "ltePSBCHIndices":
        positions = psbch_indices(**params)
        return _model(name, "R2026a LTE sidelink broadcast RE positions",
                      indices=positions, count=len(positions))
    if name == "ltePSBCHDRSIndices":
        positions = psbch_drs_indices(**params)
        return _model(name, "R2026a LTE sidelink broadcast DRS RE positions",
                      indices=positions, count=len(positions))
    if name == "lteSSSSIndices":
        positions = ssss_indices(**params)
        return _model(name, "R2026a LTE secondary sidelink sync RE positions",
                      indices=positions, count=len(positions))
    if name == "lteSSSS":
        values = ssss(**params)
        return _model(name, "R2026a LTE secondary sidelink sync sequence",
                      symbols=values, count=len(values))
    if name in ("ltePSCCHIndices", "ltePSCCHDRSIndices",
                "ltePSSCHIndices", "ltePSSCHDRSIndices"):
        channel = "PSCCH" if "PSCCH" in name else "PSSCH"
        drs = "DRS" in name
        positions, info = sidelink_channel_indices(channel, drs, **params)
        return _model(name, "R2026a LTE sidelink channel RE positions",
                      indices=positions, count=len(positions), info=info)
    if name in ("ltePSBCHDRS", "ltePSCCHDRS", "ltePSSCHDRS"):
        symbols, info = sidelink_drs(name, **params)
        return _model(name, "R2026a LTE sidelink DRS verified sequence",
                      symbols=symbols, info=info, count=len(symbols))
    if name in ("lteNSSS", "lteNSSSIndices"):
        values, positions = nsss(**params)
        return _model(name, "R2026a NB-IoT NSSS sequence and scheduled RE positions",
                      symbols=values, indices=positions, count=len(values))
    if name in ("lteNPSS", "lteNPSSIndices"):
        values, positions = npss(**params)
        return _model(name, "R2026a NB-IoT NPSS sequence and scheduled RE positions",
                      symbols=values, indices=positions, count=len(values))
    if name in ("lteNRS", "lteNRSIndices"):
        values, positions = nrs(**params)
        return _model(name, "R2026a NB-IoT NRS sequence and RE positions",
                      symbols=values, indices=positions, count=len(values))
    if name == "lteNPBCHIndices":
        positions, info = npbch_indices(**params)
        return _model(name, "R2026a NB-IoT NPBCH scheduled RE positions",
                      indices=positions, count=len(positions), info=info)
    if name == "lteNPUSCHDRSIndices":
        positions = npusch_drs_indices(**params)
        return _model(name, "R2026a NB-IoT NPUSCH DRS FDD RE positions",
                      indices=positions, count=len(positions))
    if name == "lteNPUSCHDRS":
        symbols, state = npusch_drs(**params)
        return _model(name, "R2026a NB-IoT NPUSCH Data DRS baseline sequence",
                      symbols=symbols, state=state, count=len(symbols))
    if name == "lteNPUSCHIndices":
        positions, info = npusch_indices(**params)
        return _model(name, "R2026a NB-IoT NPUSCH FDD RE positions",
                      indices=positions, count=len(positions), info=info)
    if name == "lteThroughputAnalyzer":
        blocks = np.asarray(params.get("transport_blocks", [1]), dtype=float)
        seconds = float(params.get("elapsed_seconds", 1.))
        if seconds <= 0 or np.any(blocks < 0):
            raise ValueError("elapsed_seconds must be positive and block sizes nonnegative")
        return _model(name, "headless transport-block throughput",
                      throughput_bps=float(blocks.sum()*8/seconds))
    if name in ("lteRMCDL", "lteRMCUL", "lteTestModel"):
        return _model(name, "R2026a LTE FDD/TDD reference preset configuration",
                      config=lte_preset(name, **params))
    if name in ("lteRateMatchTurbo", "lteRateRecoverTurbo", "lteTurboEncode", "lteTurboDecode"):
        return _coding(name, **params)
    if name in ("lteACKEncode", "lteRIEncode", "lteCQIEncode"):
        kind = name.removesuffix("Encode")
        coded = ul_control_encode(kind, params.get("bits", [0, 1]),
                                  qd=params.get("qd"), modulation=params.get("modulation", "QPSK"))
        return _model(name, "R2026a LTE selected PUSCH control codewords",
                      coded_bits=coded, coded_length=len(coded))
    if name in ("lteACKDecode", "lteRIDecode", "lteCQIDecode"):
        kind = name.removesuffix("Decode")
        length = int(params.get("length", params.get("payload_length", 2)))
        qd = params.get("qd")
        modulation = params.get("modulation", "QPSK")
        if params.get("soft_bits") is not None:
            soft = params["soft_bits"]
        else:
            coded = (ul_control_encode(kind, [0, 1], qd=qd, modulation=modulation)
                     if params.get("bits") is None else np.asarray(params["bits"], dtype=int))
            soft = np.where(coded >= 0, 2*coded-1, 0)
        decoded = ul_control_decode(kind, soft, length, qd=qd, modulation=modulation)
        return _model(name, "R2026a LTE selected PUSCH control codeword soft ML candidate",
                      bits=decoded, bit_length=length, block_error=False)
    if name in ("lteUCIEncode", "lteUCI3Encode"):
        kind = name.removesuffix("Encode")
        coded = uci_encode(kind, params.get("bits", [0, 1]))
        return _model(name, "R2026a LTE PUCCH UCI binary block code",
                      coded_bits=coded, coded_length=len(coded))
    if name in ("lteUCIDecode", "lteUCI3Decode"):
        kind = name.removesuffix("Decode")
        length = int(params.get("length", params.get("payload_length", 2)))
        if params.get("soft_bits") is not None:
            soft = params["soft_bits"]
        elif params.get("bits") is not None:
            soft = 2*_bits(params["bits"]).astype(float)-1
        else:
            soft = 2*uci_encode(kind, [0, 1])-1
        decoded = uci_decode(kind, soft, length)
        return _model(name, "R2026a LTE PUCCH UCI exact short-block soft ML decoding",
                      bits=decoded, bit_length=length)
    if name.startswith(("lteACK", "lteCQI", "lteRI", "lteUCI", "lteDCI", "lteSCI", "lteCFI")) and (
            name.endswith(("Encode", "Decode")) or name == "lteCFI"):
        return _control(name, **params)
    if name.endswith("ResourceGrid") or name.endswith("ResourceGridSize"):
        return _grid(name, **params)
    if name.endswith("Indices") or name.endswith(("ResourceAllocation", "Space", "Search")):
        return _indices(name, **params)
    if name.endswith("PRBS"):
        return _scrambling(name, **params)
    if name in ("lte3DChannel", "lteHSTChannel", "lteMovingChannel") or (
            name.startswith("lteSL") and "SCFDMA" in name):
        return _waveform(name, **params)
    if "ChannelEstimate" in name or "FrameOffset" in name or name.endswith("Detect"):
        return _receiver(name, **params)
    if name.endswith(("Precode", "Deprecode", "TransmitDiversityDecode")):
        return _precode(name, **params)
    if name in ("ltePRACH", "lteNPRACH") or name.endswith(("DRS", "RS", "SSS")) or name in (
            "lteCSIRS", "lteDMRS", "ltePRS", "lteNPSS", "lteNSSS", "ltePSSS", "lteSSSS"):
        return _sequence(name, **params)
    if name in ("lteCFI", "lteCFIDecode", "lteDCI", "lteSCI") or name.endswith(
            ("Encode", "Interleave", "Deinterleave")):
        return _control(name, **params)
    if name.endswith("Info") or name in ("lteDuplexingInfo",):
        if "SCFDMA" in name:
            return _waveform(name, **params)
        return _config(name, **params)
    if name.endswith("Decode"):
        return _channel(name, **params)
    if name in ("lteMIB", "lteSLMIB", "lteRMCDL", "lteRMCUL", "lteTestModel",
                "lteWarning", "evaluateGUIParameter", "saLteNscRB", "saLteParamExpand",
                "saProgressBar", "saVectorDataSource") or name.endswith(
                    ("Generator", "Tool", "GUI")):
        return _config(name, **params)
    return _channel(name, **params)
