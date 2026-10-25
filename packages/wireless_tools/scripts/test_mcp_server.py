"""End-to-end checks for the MCP adapter, including both transports."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

from mcp_server.catalog import ROOT, load_catalog
from mcp_server.server import create_server
from scripts.test_agent_e2e import extract_example_cmd


CASES = {
    "q_function": {"mode": "qfunc", "values": "[0,1]"},
    "ber_awgn": {"ebno_db": "0,5", "modulation": "bpsk"},
    "convert_snr": {"x": "6", "input_mode": "ebno", "bits_per_symbol": 2},
    "nr_tbs": {"modulation": "QPSK", "nlayers": 1, "nprb": 52, "nre-per-prb": 120, "tcr": 0.5},
    "lte_mcs": {"imcs": "17"},
    "link_capacity": {"snr_db": 0, "bandwidth_hz": 1_000_000},
}


def example_arguments(name: str) -> dict:
    schema = json.loads((ROOT / "tools" / f"{name}.schema.json").read_text(encoding="utf-8"))
    tokens = extract_example_cmd(schema)
    if not tokens or not tokens[0].endswith(f"{name}.py"):
        raise ValueError(f"bad example command for {name}")
    spec = load_catalog({name})[name]
    fields = spec.input_schema["properties"]
    arguments: dict = {}
    i = 1
    while i < len(tokens):
        token = tokens[i]
        if not token.startswith("--"):
            if "command" in arguments:
                raise ValueError(f"multiple subcommands for {name}")
            arguments["command"] = token
            i += 1
            continue
        key = token[2:]
        if key not in fields:
            raise ValueError(f"unknown example flag for {name}: {key}")
        kind = fields[key]["type"]
        if kind == "boolean":
            arguments[key] = True
            i += 1
            continue
        if i + 1 >= len(tokens):
            raise ValueError(f"missing example value for {name}.{key}")
        raw = tokens[i + 1]
        arguments[key] = int(raw) if kind == "integer" else float(raw) if kind == "number" else raw
        i += 2
    return arguments


def direct_cli(name: str, arguments: dict) -> dict:
    spec = load_catalog()[name]
    cmd = [sys.executable, str(spec.script)]
    for field, value in arguments.items():
        if isinstance(value, bool):
            if value:
                cmd.append(f"--{field}")
        else:
            cmd.extend((f"--{field}", str(value)))
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_lte_validated_subset_over_mcp(self) -> None:
        oracle = ROOT / "matlab_oracle" / "samples"
        turbo = json.loads((oracle / "lte_turbo.json").read_text(encoding="utf-8"))[0]
        nrs = json.loads((oracle / "lte_nrs.json").read_text(encoding="utf-8"))[1]
        npbch = json.loads((oracle / "lte_npbch_indices.json").read_text(encoding="utf-8"))[1]
        drs = json.loads((oracle / "lte_npusch_drs_indices.json").read_text(encoding="utf-8"))[0]
        mib = json.loads((oracle / "lte_mib.json").read_text(encoding="utf-8"))[1]
        sl_mib = json.loads((oracle / "lte_sl_mib.json").read_text(encoding="utf-8"))[3]
        npusch = json.loads((oracle / "lte_npusch_indices.json").read_text(encoding="utf-8"))[0]
        psss = next(case for case in json.loads((oracle / "lte_psss.json").read_text(encoding="utf-8"))
                    if case["kind"] == "indices" and case["nrb"] == 50
                    and case["cyclic_prefix"] == "Normal")
        prbs = next(case for case in json.loads((oracle / "lte_control_prbs.json").read_text(encoding="utf-8"))
                    if case["entry"] == "ltePCFICHPRBS" and case["ncellid"] == 37
                    and case["nsubframe"] == 4)
        duplex = json.loads((oracle / "lte_duplexing.json").read_text(encoding="utf-8"))[3]
        pbch = json.loads((oracle / "lte_pbch_indices.json").read_text(encoding="utf-8"))[0]
        nb_downlink = json.loads((oracle / "lte_nb_downlink_indices.json").read_text(encoding="utf-8"))[0]
        psbch_drs = json.loads((oracle / "lte_psbch_drs_indices.json").read_text(encoding="utf-8"))[0]
        ssss = json.loads((oracle / "lte_ssss.json").read_text(encoding="utf-8"))[0]
        sl_indices = json.loads((oracle / "lte_sidelink_indices.json").read_text(encoding="utf-8"))[0]
        sl_prbs = json.loads((oracle / "lte_remaining_prbs.json").read_text(encoding="utf-8"))[0]
        srs = json.loads((oracle / "lte_srs_info.json").read_text(encoding="utf-8"))[17]
        phich = json.loads((oracle / "lte_phich_info.json").read_text(encoding="utf-8"))[20]
        pdcch = json.loads((oracle / "lte_pdcch_info.json").read_text(encoding="utf-8"))[100]
        perm = json.loads((oracle / "lte_pdcch_interleave.json").read_text(encoding="utf-8"))[1]
        dci_coding = json.loads((oracle / "lte_dci_coding.json").read_text(encoding="utf-8"))[0]
        dlsch = json.loads((oracle / "lte_dlsch_info.json").read_text(encoding="utf-8"))[1]
        sci_coding = json.loads((oracle / "lte_sci_coding.json").read_text(encoding="utf-8"))[0]
        ulsch_perm = json.loads((oracle / "lte_ulsch_interleave.json").read_text(encoding="utf-8"))[0]
        bch = json.loads((oracle / "lte_bch.json").read_text(encoding="utf-8"))[0]
        slbch = json.loads((oracle / "lte_slbch.json").read_text(encoding="utf-8"))[0]
        prach = json.loads((oracle / "lte_prach_info.json").read_text(encoding="utf-8"))[0]
        nprach = json.loads((oracle / "lte_nprach_info.json").read_text(encoding="utf-8"))[0]
        uci_cases = json.loads((oracle / "lte_uci_codes.json").read_text(encoding="utf-8"))
        uci = next(case for case in uci_cases if case["entry"] == "lteUCI" and case["n"] == 5)["trials"][0]
        uci3 = next(case for case in uci_cases if case["entry"] == "lteUCI3" and case["n"] == 8)["trials"][0]
        control_re = json.loads((oracle / "lte_control_indices.json").read_text(encoding="utf-8"))
        pdcch_re = next(case for case in control_re if case["entry"] == "ltePDCCHIndices"
                        and case["nrb"] == 25 and case["ncellid"] == 37
                        and case["ports"] == 2 and case["cfi"] == 2)
        phich_re = next(case for case in control_re if case["entry"] == "ltePHICHIndices"
                        and case["nrb"] == 6 and case["ncellid"] == 0
                        and case["ports"] == 1 and case["cfi"] == 1)
        sl_drs = json.loads((oracle / "lte_sidelink_drs.json").read_text(encoding="utf-8"))
        drs_psbch = sl_drs[167]
        drs_pscch = next(case for case in sl_drs if case["entry"] == "ltePSCCHDRS")
        drs_pssch = next(case for case in sl_drs if case["entry"] == "ltePSSCHDRS")
        preset_cases = json.loads((oracle / "lte_presets.json").read_text(encoding="utf-8"))["records"]
        dl_preset = next(case for case in preset_cases if case["entry"] == "lteRMCDL"
                         and case["name"] == "R.0" and case["duplex"] == "FDD")
        ul_preset = next(case for case in preset_cases if case["entry"] == "lteRMCUL"
                         and case["name"] == "A1-1" and case["duplex"] == "TDD")
        tm_preset = next(case for case in preset_cases if case["entry"] == "lteTestModel"
                         and case["name"] == "1.1" and case["bandwidth"] == "5MHz"
                         and case["duplex"] == "FDD")
        reference_cases = json.loads((oracle / "lte_reference_signals.json").read_text(encoding="utf-8"))
        csirs = next(case for case in reference_cases if case["entry"] == "lteCSIRS"
                     and case["nrb"] == 6 and case["ncellid"] == 37
                     and case["nsubframe"] == 1 and case["csi_ref_ports"] == 2)
        prs = next(case for case in reference_cases if case["entry"] == "ltePRS"
                   and case["nrb"] == 25 and case["ncellid"] == 0
                   and case["nsubframe"] == 4)
        pucch_indices_cases = json.loads((oracle / "lte_pucch_indices.json").read_text(encoding="utf-8"))
        pucch_idx = next(case for case in pucch_indices_cases if case["entry"] == "ltePUCCH1Indices"
                         and case["nrb"] == 25 and case["ncellid"] == 37
                         and case["nsubframe"] == 3 and case["cyclic_prefix"] == "Normal"
                         and case["resource_idx"] == 5)
        pucch_drs_idx = next(case for case in pucch_indices_cases if case["entry"] == "ltePUCCH3DRSIndices"
                             and case["nrb"] == 6 and case["ncellid"] == 0
                             and case["nsubframe"] == 0 and case["cyclic_prefix"] == "Normal"
                             and case["resource_idx"] == 0)
        pucch_drs_cases = json.loads((oracle / "lte_pucch_drs.json").read_text(encoding="utf-8"))
        pucch_drs = next(case for case in pucch_drs_cases if case["entry"] == "ltePUCCH2DRS"
                         and case["nrb"] == 6 and case["ncellid"] == 0
                         and case["nsubframe"] == 0 and case["cyclic_prefix"] == "Normal"
                         and case["resource_idx"] == 0 and case["ack"] == [0, 1])
        ul_control_cases = json.loads((oracle / "lte_ul_control_codes.json").read_text(encoding="utf-8"))
        ack_control = next(case for case in ul_control_cases if case["entry"] == "lteACK"
                           and case["n"] == 2 and case["qd"] == 4
                           and case["modulation"] == "QPSK")["trials"][0]
        ri_control = next(case for case in ul_control_cases if case["entry"] == "lteRI"
                          and case["n"] == 2 and case["qd"] == 4
                          and case["modulation"] == "QPSK")["trials"][0]
        cqi_control = next(case for case in ul_control_cases if case["entry"] == "lteCQI"
                           and case["n"] == 5 and case["qd"] == 16
                           and case["modulation"] == "QPSK")["trials"][0]
        dmrs_cases = json.loads((oracle / "lte_dmrs.json").read_text(encoding="utf-8"))
        pdsch_dmrs = next(case for case in dmrs_cases if case["entry"] == "lteDMRS"
                          and case["nrb"] == 6 and case["ncellid"] == 0
                          and case["nsubframe"] == 0 and case["prb_set"] == 0
                          and case["rnti"] == 1)
        epdcch_dmrs = next(case for case in dmrs_cases if case["entry"] == "lteEPDCCHDMRS"
                           and case["nrb"] == 6 and case["ncellid"] == 0
                           and case["nsubframe"] == 0 and case["prb_set"] == 0
                           and case["epdcch_nid"] == 0)
        epdcch_data = json.loads((oracle / "lte_epdcch_indices.json").read_text(encoding="utf-8"))["records"][0]
        npusch_drs_symbols = json.loads((oracle / "lte_npusch_drs.json").read_text(encoding="utf-8"))[0]
        requests = (
            ("lte_misc_family", "lteTurboEncode", {"bits": turbo["bits"]},
             "coded_bits", turbo["coded"]),
            ("lte_nb_family", "lteNRSIndices",
             {"nncellid": nrs["config"]["NNCellID"],
              "nsubframe": nrs["config"]["NSubframe"],
              "nb_ref_ports": nrs["config"]["NBRefP"], "index_base": 1},
             "indices", nrs["indices"]),
            ("lte_nb_family", "lteNBResourceGrid", {"nb_ref_ports": 2},
             "size", [12, 14, 2]),
            ("lte_nb_family", "lteNPBCHIndices",
             {"nncellid": npbch["config"]["NNCellID"],
              "nb_ref_ports": npbch["config"]["NBRefP"], "index_base": 1},
             "indices", npbch["indices"]),
            ("lte_nb_family", "lteNPUSCHDRSIndices",
             {"spacing_khz": 15, "npusch_format": drs["channel"]["NPUSCHFormat"],
              "subcarrier_set": drs["channel"]["NBULSubcarrierSet"], "index_base": 1},
             "indices", drs["indices"]),
            ("lte_nb_family", "lteNPUSCHIndices",
             {"spacing_khz": 15, "npusch_format": npusch["channel"]["NPUSCHFormat"],
              "subcarrier_set": npusch["channel"]["NBULSubcarrierSet"],
              "nru": npusch["channel"]["NRU"],
              "nul_slots": npusch["channel"]["NULSlots"],
              "modulation": npusch["channel"]["Modulation"], "index_base": 1},
             "indices", npusch["indices"]),
            ("lte_misc_family", "lteMIB", {"fields": mib["config"]},
             "bits", mib["bits"]),
            ("lte_sidelink_family", "lteSLMIB", {"fields": sl_mib["config"]},
             "bits", sl_mib["bits"]),
            ("lte_sidelink_family", "ltePSSSIndices",
             {"nrb": psss["nrb"], "cyclic_prefix": psss["cyclic_prefix"],
              "index_base": 1}, "indices", psss["indices"]),
            ("lte_downlink_family", "ltePCFICHPRBS",
             {"ncellid": prbs["ncellid"], "nsubframe": prbs["nsubframe"],
              "length": 32}, "bits", prbs["bits"]),
            ("lte_downlink_family", "ltePCFICHInfo", {},
             "info", {"NREG": 4, "NRE": 16}),
            ("lte_downlink_family", "lteDuplexingInfo",
             {"duplex_mode": duplex["config"]["DuplexMode"],
              "tdd_config": duplex["config"]["TDDConfig"],
              "nsubframe": duplex["config"]["NSubframe"], "ssc": 0},
             "info", duplex["info"]),
            ("lte_downlink_family", "ltePBCHIndices",
             {"nrb": pbch["config"]["NDLRB"],
              "ncellid": pbch["config"]["NCellID"], "index_base": 1},
             "indices", pbch["indices"]),
            ("lte_nb_family", "lteNPDSCHIndices",
             {"nncellid": nb_downlink["enb"]["NNCellID"],
              "nb_ref_ports": nb_downlink["enb"]["NBRefP"],
              "nsf": nb_downlink["channel"]["NSF"], "index_base": 1},
             "indices", nb_downlink["indices"]),
            ("lte_sidelink_family", "ltePSBCHDRSIndices",
             {"nrb": psbch_drs["nrb"], "sidelink_mode": psbch_drs["mode"],
              "cyclic_prefix": psbch_drs["cyclic_prefix"], "index_base": 1},
             "indices", psbch_drs["indices"]),
            ("lte_sidelink_family", "lteSSSS",
             {"nslid": ssss["nslid"], "sidelink_mode": ssss["mode"]},
             "symbols", {"real": ssss["real"], "imag": [0]*124}),
            ("lte_sidelink_family", sl_indices["entry"],
             {"nrb": sl_indices["config"]["NSLRB"],
              "prb_set": sl_indices["config"]["PRBSet"],
              "sidelink_mode": sl_indices["config"]["SidelinkMode"],
              "index_base": 1}, "indices", sl_indices["indices"]),
            ("lte_sidelink_family", sl_prbs["entry"],
             {"nslid": sl_prbs["config"]["NSLID"], "length": 32},
             "bits", sl_prbs["bits"]),
            ("lte_uplink_family", "lteSRSInfo",
             {"subframe_config": srs["config"], "duplex_mode": srs["mode"],
              "nsubframe": 2}, "info",
             {"CellPeriod": srs["period"], "CellOffset": srs["offset"],
              "IsSRSSubframe": srs["scheduled"][2]}),
            ("lte_downlink_family", "ltePHICHInfo",
             {"nrb": phich["nrb"], "ng": phich["ng"],
              "cyclic_prefix": phich["cyclic_prefix"],
              "phich_duration": phich["phich_duration"]},
             "info", phich["info"]),
            ("lte_downlink_family", "ltePDCCHInfo",
             {"nrb": pdcch["nrb"], "ng": pdcch["ng"],
              "cyclic_prefix": pdcch["cyclic_prefix"], "ports": pdcch["ports"],
              "cfi": pdcch["cfi"]}, "info", pdcch["info"]),
            ("lte_downlink_family", "ltePDCCHInterleave",
             {"symbols": list(range(1, 4*perm["reg"]+1)),
              "ncellid": perm["ncellid"]}, "symbols", perm["forward"]),
            ("lte_downlink_family", "lteDLSCHInfo",
             {"block_length": dlsch["block_length"]}, "info", dlsch["info"]),
            ("lte_downlink_family", "lteDCIEncode",
             {"bits": dci_coding["bits"], "pdcch_format": dci_coding["format"],
              "rnti": dci_coding["rnti"]}, "coded_bits", dci_coding["coded"]),
            ("lte_downlink_family", "lteBCH",
             {"bits": bch["bits"], "cyclic_prefix": bch["cp"],
              "ports": bch["ports"]}, "coded_bits", bch["coded"]),
            ("lte_uplink_family", "lteULSCHInterleave",
             {"bits": ulsch_perm["data"], "cyclic_prefix": ulsch_perm["cp"],
              "shortened": ulsch_perm["shortened"],
              "modulation": ulsch_perm["modulation"]},
             "bits", ulsch_perm["interleaved"]),
            ("lte_sidelink_family", "lteSCIEncode",
             {"bits": sci_coding["bits"], "nrb": sci_coding["config"]["NSLRB"],
              "sidelink_mode": sci_coding["config"]["SidelinkMode"],
              "cyclic_prefix": sci_coding["config"]["CyclicPrefixSL"]},
             "coded_bits", sci_coding["coded"]),
            ("lte_sidelink_family", "lteSLBCH",
             {"bits": slbch["bits"],
              "sidelink_mode": slbch["config"]["SidelinkMode"],
              "cyclic_prefix": slbch["config"]["CyclicPrefixSL"]},
             "coded_bits", slbch["coded"]),
            ("lte_waveform_family", "ltePRACHInfo",
             {"nrb": prach["nrb"], "preamble_format": prach["format"]},
             "info", prach["info"]),
            ("lte_nb_family", "lteNPRACHInfo",
             {"nncellid": nprach["cellid"],
              "spacing_khz": float(nprach["spacing"].replace("kHz", "")),
              "nprach_format": nprach["format"]}, "info", nprach["info"]),
            ("lte_uplink_family", "lteUCIEncode", {"bits": uci["bits"]},
             "coded_bits", uci["coded"]),
            ("lte_uplink_family", "lteUCIDecode",
             {"soft_bits": [2*bit-1 for bit in uci["coded"]], "length": 5},
             "bits", uci["bits"]),
            ("lte_uplink_family", "lteUCI3Encode", {"bits": uci3["bits"]},
             "coded_bits", uci3["coded"]),
            ("lte_uplink_family", "lteUCI3Decode",
             {"soft_bits": [2*bit-1 for bit in uci3["coded"]], "length": 8},
             "bits", uci3["bits"]),
            ("lte_downlink_family", "ltePDCCHIndices",
             {"nrb": 25, "ncellid": 37, "ports": 2, "cfi": 2, "index_base": 1},
             "indices", pdcch_re["indices"]),
            ("lte_downlink_family", "ltePHICHIndices",
             {"nrb": 6, "ncellid": 0, "ports": 1, "cfi": 1, "index_base": 1},
             "indices", phich_re["indices"]),
            ("lte_sidelink_family", "ltePSBCHDRS", {"nslid": 167},
             "info", drs_psbch["info"]),
            ("lte_sidelink_family", "ltePSCCHDRS",
             {"nrb": 15, "prb_set": [5], "sidelink_mode": "D2D"},
             "info", drs_pscch["info"]),
            ("lte_sidelink_family", "ltePSSCHDRS",
             {"nrb": 50, "prb_set": [30, 31], "nsaid": 37},
             "info", drs_pssch["info"]),
            ("lte_waveform_family", "lteRMCDL", {"rc": "R.0"},
             "config", dl_preset["config"]),
            ("lte_waveform_family", "lteRMCUL",
             {"rc": "A1-1", "duplex_mode": "TDD"},
             "config", ul_preset["config"]),
            ("lte_waveform_family", "lteTestModel",
             {"tmn": "1.1", "bandwidth": "5MHz"},
             "config", tm_preset["config"]),
            ("lte_downlink_family", "lteCSIRS",
             {"nrb": 6, "ncellid": 37, "nsubframe": 1, "csi_ref_ports": 2},
             "symbols", {"real": csirs["real"], "imag": csirs["imag"]}),
            ("lte_downlink_family", "ltePRSIndices",
             {"nrb": 25, "ncellid": 0, "nsubframe": 4, "index_base": 1},
             "indices", prs["indices"]),
            ("lte_uplink_family", "ltePUCCH1Indices",
             {"nrb": 25, "ncellid": 37, "nsubframe": 3,
              "cyclic_prefix": "Normal", "resource_idx": 5, "index_base": 1},
             "indices", pucch_idx["indices"]),
            ("lte_uplink_family", "ltePUCCH3DRSIndices", {"index_base": 1},
             "indices", pucch_drs_idx["indices"]),
            ("lte_uplink_family", "ltePUCCH2DRS", {"ack": [0, 1]},
             "info", pucch_drs["info"]),
            ("lte_uplink_family", "lteACKEncode", {"bits": ack_control["bits"]},
             "coded_bits", ack_control["coded"]),
            ("lte_uplink_family", "lteACKDecode",
             {"soft_bits": [2*bit-1 for bit in ack_control["coded"]], "length": 2},
             "bits", ack_control["bits"]),
            ("lte_uplink_family", "lteRIEncode", {"bits": ri_control["bits"]},
             "coded_bits", ri_control["coded"]),
            ("lte_uplink_family", "lteRIDecode",
             {"soft_bits": [2*bit-1 for bit in ri_control["coded"]], "length": 2},
             "bits", ri_control["bits"]),
            ("lte_uplink_family", "lteCQIEncode", {"bits": cqi_control["bits"]},
             "coded_bits", cqi_control["coded"]),
            ("lte_uplink_family", "lteCQIDecode",
             {"soft_bits": [2*bit-1 for bit in cqi_control["coded"]], "length": 5},
             "bits", cqi_control["bits"]),
            ("lte_downlink_family", "lteDMRS",
             {"nrb": 6, "ncellid": 0, "nsubframe": 0,
              "prb_set": [0], "rnti": 1},
             "symbols", {"real": pdsch_dmrs["real"], "imag": pdsch_dmrs["imag"]}),
            ("lte_downlink_family", "lteDMRSIndices",
             {"nrb": 6, "ncellid": 0, "nsubframe": 0,
              "prb_set": [0], "rnti": 1, "index_base": 1},
             "indices", pdsch_dmrs["indices"]),
            ("lte_downlink_family", "lteEPDCCHDMRS",
             {"nrb": 6, "ncellid": 0, "nsubframe": 0,
              "prb_set": [0], "epdcch_nid": 0},
             "symbols", {"real": epdcch_dmrs["real"], "imag": epdcch_dmrs["imag"]}),
            ("lte_downlink_family", "lteEPDCCHDMRSIndices",
             {"nrb": 6, "ncellid": 0, "nsubframe": 0,
              "prb_set": [0], "epdcch_nid": 0, "index_base": 1},
             "indices", epdcch_dmrs["indices"]),
            ("lte_downlink_family", "lteEPDCCHIndices",
             {"nrb": epdcch_data["nrb"], "ncellid": epdcch_data["ncellid"],
              "nsubframe": epdcch_data["nsubframe"],
              "prb_set": epdcch_data["prb_set"], "cfi": epdcch_data["cfi"],
              "epdcch_type": epdcch_data["epdcch_type"], "index_base": 1},
             "indices", epdcch_data["indices"]),
            ("lte_nb_family", "lteNPUSCHDRS",
             {"spacing_khz": float(npusch_drs_symbols["spacing"].replace("kHz", "")),
              "subcarrier_set": npusch_drs_symbols["subcarriers"],
              "nncellid": npusch_drs_symbols["ncellid"],
              "nslot": npusch_drs_symbols["slot"],
              "nul_slots": npusch_drs_symbols["nul_slots"]},
             "state", npusch_drs_symbols["state"]),
        )
        async with Client(create_server(only={"lte_misc_family", "lte_nb_family",
                                              "lte_sidelink_family", "lte_uplink_family",
                                              "lte_downlink_family", "lte_waveform_family"})) as client:
            for tool, function, params, field, expected in requests:
                with self.subTest(function=function):
                    result = await client.call_tool(tool, {"function": function,
                                                          "params": json.dumps(params)})
                    self.assertFalse(result.is_error, str(result.content))
                    self.assertEqual(result.structured_content["result"][field], expected)

    async def test_all_registered_examples_over_mcp(self) -> None:
        catalog = load_catalog()
        registered = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))["tools"]
        self.assertEqual(len(catalog), len(registered))
        with tempfile.TemporaryDirectory(prefix="wireless-mcp-test-") as temp:
            async with Client(create_server(data_root=Path(temp)), read_timeout_seconds=45) as client:
                tools = (await client.list_tools()).tools
                self.assertEqual({tool.name for tool in tools}, set(catalog))
                for name in catalog:
                    with self.subTest(name=name):
                        result = await client.call_tool(name, example_arguments(name))
                        self.assertFalse(result.is_error, f"{name}: {result.content}")
                        self.assertIsInstance(result.structured_content, dict)

    async def test_pilot_tools_match_cli(self) -> None:
        async with Client(create_server()) as client:
            for name, args in CASES.items():
                with self.subTest(name=name):
                    result = await client.call_tool(name, args)
                    self.assertFalse(result.is_error)
                    self.assertEqual(result.structured_content, direct_cli(name, args))
            differential = {"ebno_db": "0", "modulation": "bpsk", "differential": True}
            result = await client.call_tool("ber_awgn", differential)
            self.assertEqual(result.structured_content, direct_cli("ber_awgn", differential))

    async def test_validation_and_tool_error(self) -> None:
        async with Client(create_server()) as client:
            invalid = await client.call_tool("link_capacity", {"snr_db": 0, "bandwidth_hz": 1, "extra": 1})
            self.assertTrue(invalid.is_error)
            self.assertEqual(json.loads(invalid.content[0].text)["code"], "INVALID_ARGUMENT")
            missing = await client.call_tool("q_function", {"mode": "qfunc"})
            self.assertTrue(missing.is_error)
            self.assertEqual(json.loads(missing.content[0].text)["code"], "INVALID_ARGUMENT")
            failed = await client.call_tool("q_function", {"mode": "qfuncinv", "values": "2"})
            self.assertTrue(failed.is_error)
            self.assertEqual(json.loads(failed.content[0].text)["code"], "TOOL_ERROR")
            infinite = await client.call_tool("q_function", {"mode": "qfuncinv", "values": "0"})
            self.assertFalse(infinite.is_error)
            self.assertEqual(infinite.structured_content, {"output": ["Infinity"]})
            subcommand = await client.call_tool("wireless_utils", {"command": "biterr", "x": "0,1", "y": "0,0"})
            self.assertFalse(subcommand.is_error)
            self.assertEqual(subcommand.structured_content["num_errors"], 1)
            for arguments in (
                {"command": "awgn", "signal": "1,0", "snr": 10},
                {"command": "berawgn", "ebn0": 0, "mod": "bpsk"},
                {"command": "bcc-interleave", "bits": "0,1,0,1", "ncbps": 4},
                {"command": "golay", "length": 32},
            ):
                with self.subTest(command=arguments["command"]):
                    result = await client.call_tool("wireless_utils", arguments)
                    self.assertFalse(result.is_error, str(result.content))
            scramble = await client.call_tool(
                "nr_dci", {"command": "scramble", "dci-bits": "1,0,1,1", "rnti": 4660, "n-id": 1}
            )
            self.assertFalse(scramble.is_error, str(scramble.content))
            inverse = await client.call_tool(
                "nr_modulation", {"mod": "BPSK", "inverse": True, "symbols": "[1]"}
            )
            self.assertFalse(inverse.is_error, str(inverse.content))
            mcs = await client.call_tool("nr_mcs_tables", {"table": "QAM256Table", "mcs": 0})
            self.assertFalse(mcs.is_error, str(mcs.content))
            bad_subcommand = await client.call_tool("wireless_utils", {"command": "biterr", "signal": "1"})
            self.assertTrue(bad_subcommand.is_error)
            self.assertEqual(json.loads(bad_subcommand.content[0].text)["code"], "INVALID_ARGUMENT")
            escaped = await client.call_tool("awgn", {"signal_file": "../secret.json", "snr": 1})
            self.assertTrue(escaped.is_error)
            self.assertEqual(json.loads(escaped.content[0].text)["code"], "INVALID_PATH")

    async def test_selected_tool_subset(self) -> None:
        async with Client(create_server(only={"q_function", "nr_tbs"})) as client:
            self.assertEqual(
                {tool.name for tool in (await client.list_tools()).tools}, {"q_function", "nr_tbs"}
            )

    async def test_negative_vector_argument(self) -> None:
        async with Client(create_server(only={"node_mobility_constant_velocity"})) as client:
            result = await client.call_tool("node_mobility_constant_velocity", {
                "initial_position": "10,5,0", "velocity": "-1,2,0", "times": "0,4,8",
            })
            self.assertFalse(result.is_error, str(result.content))
            self.assertEqual(result.structured_content["positions"], [
                [10.0, 5.0, 0.0], [6.0, 13.0, 0.0], [2.0, 21.0, 0.0],
            ])

    async def test_file_modes_stay_in_data_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wireless-mcp-files-") as temp:
            root = Path(temp)
            (root / "input.json").write_text(
                json.dumps({"distance": [1, 10], "environment": "Industrial", "standard_deviation": 0}),
                encoding="utf-8",
            )
            (root / "bad.json").write_text(
                '{"operation":"create_session","session_file":"../outside.sqlite"}', encoding="utf-8"
            )
            async with Client(create_server(data_root=root)) as client:
                loaded = await client.call_tool("bluetooth_path_loss", {"input_file": "input.json"})
                self.assertFalse(loaded.is_error, str(loaded.content))
                exported = await client.call_tool(
                    "bluetooth_classic_waveform",
                    {"input": '{"message":[1,0,1,0],"properties":{"packet_type":"NULL"}}',
                     "output_file": "wave.npz"},
                )
                self.assertFalse(exported.is_error, str(exported.content))
                self.assertTrue((root / "wave.npz").is_file())
                capture = await client.call_tool(
                    "ble_pcap_writer",
                    {"input": json.dumps({"file_extension": "pcapng", "packets": [
                        {"packet": "D6BE898E4009AB8967452301020106A8F1DF", "timestamp_us": 0}
                    ], "output_path": "capture.pcapng"})},
                )
                self.assertFalse(capture.is_error, str(capture.content))
                self.assertTrue((root / "capture.pcapng").is_file())
                escaped = await client.call_tool(
                    "bluetooth_session",
                    {"input": '{"operation":"create_session","session_file":"../outside.sqlite"}'},
                )
                self.assertTrue(escaped.is_error)
                self.assertEqual(json.loads(escaped.content[0].text)["code"], "INVALID_PATH")
                escaped_file = await client.call_tool("bluetooth_session", {"input_file": "bad.json"})
                self.assertTrue(escaped_file.is_error)
                self.assertEqual(json.loads(escaped_file.content[0].text)["code"], "INVALID_PATH")
                created = await client.call_tool(
                    "bluetooth_session",
                    {"input": '{"operation":"create_session","session_file":"state.sqlite"}'},
                )
                self.assertFalse(created.is_error, str(created.content))
                self.assertTrue((root / "state.sqlite").is_file())

    async def test_stdio_subprocess(self) -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server"],
            cwd=str(ROOT),
        )
        async with Client(params) as client:
            self.assertEqual(len((await client.list_tools()).tools), len(load_catalog()))
            result = await client.call_tool("lte_mcs", {"imcs": "17"})
            self.assertFalse(result.is_error)
            self.assertEqual(result.structured_content["itbs"], 15)

    async def test_streamable_http(self) -> None:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        process = subprocess.Popen(
            [sys.executable, "-m", "mcp_server", "--transport", "streamable-http", "--port", str(port)],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=os.environ.copy(),
        )
        try:
            for _ in range(100):
                if process.poll() is not None:
                    self.fail(f"HTTP server exited with code {process.returncode}")
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                        break
                except OSError:
                    await asyncio.sleep(0.1)
            else:
                self.fail("HTTP server did not start")
            async with Client(f"http://127.0.0.1:{port}/mcp") as client:
                self.assertEqual(len((await client.list_tools()).tools), len(load_catalog()))
                result = await client.call_tool("link_capacity", CASES["link_capacity"])
                self.assertFalse(result.is_error)
                self.assertEqual(result.structured_content["capacity_bps"], 1_000_000)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
