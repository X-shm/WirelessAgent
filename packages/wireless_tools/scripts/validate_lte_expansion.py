"""Check all newly mapped LTE entry points and representative numerical invariants."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from _lte_expansion_core import GROUPS, execute


def main():
    errors = []
    names = [name for group in GROUPS.values() for name in group]
    for name in names:
        params = ({"value": 2} if name == "evaluateGUIParameter" else
                  {"waveform": {"real": [0]*1920, "imag": [0]*1920}}
                  if name == "lteSLSCFDMADemodulate" else {})
        try:
            result = execute(name, **params)
            assert result["entry"] == name and result["model"], result
        except (ValueError, TypeError, KeyError, AssertionError, ZeroDivisionError) as exc:
            errors.append((name, str(exc)))
    assert not errors, errors

    register = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))["tools"]
    registered = {entry["name"]: entry for entry in register}
    for family, members in GROUPS.items():
        tool = f"lte_{family}_family"
        schema = json.loads((ROOT / "tools" / f"{tool}.schema.json").read_text(encoding="utf-8"))
        assert set(members) == set(registered[tool]["source_functions"]) == set(
            schema["inputs"]["function"]["enum"])
        command = schema["example"]["cmd"].split("--function ", 1)[1].split(" ", 1)[0]
        assert command in members
        assert registered[tool]["status"] == "partial"
    inventory = json.loads((ROOT / "references" / "function_inventory.json").read_text(encoding="utf-8"))
    public = {entry["matlab_name"] for entry in inventory["products"]["LTE Toolbox"]["functions"]}
    sources = [source for entry in register if entry["product"] == "LTE Toolbox"
               for source in entry["source_functions"]]
    prior = [source for entry in register if entry["product"] != "LTE Toolbox"
             for source in entry["source_functions"] if source in public]
    assert len(names) == len(set(names)) == 212
    assert len(public) == 273 and set(sources) | set(prior) == public
    assert len(set(sources) | set(prior)) == len(public)
    inventory_status = {entry["matlab_name"]: entry["status"]
                        for entry in inventory["products"]["LTE Toolbox"]["functions"]}
    validated = {"lteNPSS", "lteNPSSIndices", "lteNSSS", "lteNSSSIndices",
                 "lteNRS", "lteNRSIndices", "lteNBResourceGrid", "lteNPBCHIndices",
                 "lteNPUSCHDRSIndices", "lteNPUSCHIndices",
                 "lteNPDSCHIndices", "lteNPDCCHIndices", "lteNPRACHInfo",
                 "lteNPUSCHDRS",
                 "lteTurboEncode", "lteTurboDecode", "lteMIB", "lteSLMIB",
                 "ltePSSS", "ltePSSSIndices", "lteSSSS", "ltePSBCHIndices",
                 "ltePSBCHDRSIndices", "lteSSSSIndices",
                 "ltePSCCHIndices", "ltePSCCHDRSIndices",
                 "ltePSSCHIndices", "ltePSSCHDRSIndices",
                 "ltePSBCHPRBS", "ltePSCCHPRBS", "ltePSSCHPRBS",
                 "ltePSBCH", "ltePSCCH", "ltePSSCH",
                 "ltePSBCHDRS", "ltePSCCHDRS", "ltePSSCHDRS",
                 "ltePSBCHDecode", "ltePSCCHDecode", "ltePSSCHDecode",
                 "lteSCIInfo", "lteSCIEncode", "lteSCIDecode", "lteSLSCFDMAInfo",
                 "lteSLBCH", "lteSLBCHDecode",
                 "ltePUCCH2PRBS", "ltePUCCH3PRBS", "lteSRSInfo",
                 "lteULSCHInterleave", "lteULSCHDeinterleave",
                 "lteULPMIInfo", "ltePUSCHPrecode", "ltePUSCHDeprecode",
                 "lteUCIEncode", "lteUCIDecode", "lteUCI3Encode", "lteUCI3Decode",
                 "ltePUCCH1Indices", "ltePUCCH1DRSIndices", "ltePUCCH1DRS",
                 "ltePUCCH2Indices", "ltePUCCH2DRSIndices", "ltePUCCH2DRS",
                 "ltePUCCH3Indices", "ltePUCCH3DRSIndices", "ltePUCCH3DRS",
                 "lteACKEncode", "lteACKDecode", "lteRIEncode", "lteRIDecode",
                 "lteCQIEncode", "lteCQIDecode",
                 "lteRateMatchTurbo", "lteRateRecoverTurbo", "saLteNscRB",
                 "lteCFI", "lteCFIDecode",
                 "lteDLResourceGrid", "lteDLResourceGridSize",
                 "lteULResourceGrid", "lteULResourceGridSize",
                 "lteSLResourceGrid", "lteSLResourceGridSize",
                 "ltePBCHPRBS", "ltePDCCHPRBS", "ltePCFICHPRBS",
                 "ltePHICHPRBS", "lteEPDCCHPRBS",
                 "ltePCFICHIndices", "ltePCFICHInfo", "ltePCFICH", "ltePCFICHDecode",
                 "ltePHICHInfo", "ltePDCCHInfo", "ltePDCCHIndices", "ltePHICHIndices",
                 "lteCSIRS", "lteCSIRSIndices", "ltePRS", "ltePRSIndices",
                 "lteDMRS", "lteDMRSIndices", "lteEPDCCHDMRS",
                 "lteEPDCCHDMRSIndices", "lteEPDCCHIndices",
                 "ltePDCCHInterleave",
                 "ltePDCCHDeinterleave", "lteDLSCHInfo", "lteDCIEncode",
                 "lteDCIDecode", "lteDCIInfo", "ltePRACHInfo",
                 "lteRMCDL", "lteRMCUL", "lteTestModel",
                 "lteBCH", "lteBCHDecode",
                 "ltePBCH", "ltePBCHDecode",
                 "lteDuplexingInfo", "ltePBCHIndices"}
    assert all(inventory_status[name] == "validated_subset" for name in validated)
    assert inventory_status["lte3DChannel"] == "partial"

    uci_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_uci_codes.json").read_text(encoding="utf-8"))
    for case in uci_cases:
        name, length = case["entry"], case["n"]
        for trial in case["trials"]:
            bits = np.atleast_1d(trial["bits"]).astype(int).tolist()
            coded = execute(name+"Encode", bits=bits)["coded_bits"]
            assert coded == trial["coded"], (name, length, bits)
            if "decoded" in trial and length <= 11:
                soft = 2*np.asarray(coded, dtype=float)-1
                decoded = execute(name+"Decode", soft_bits=soft.tolist(), length=length)["bits"]
                assert decoded == np.atleast_1d(trial["decoded"]).astype(int).tolist()
                noisy = execute(name+"Decode", soft_bits=trial["noisy_soft"],
                                length=length)["bits"]
                assert noisy == np.atleast_1d(trial["noisy_decoded"]).astype(int).tolist()
    for name, length in (("lteUCI", 12), ("lteUCI3", 22)):
        try:
            execute(name+"Decode", soft_bits=[0]*(20 if name == "lteUCI" else 48),
                    length=length)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{name} decoder must reject unsupported payload lengths")

    control_indices_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_control_indices.json").read_text(encoding="utf-8"))
    for case in control_indices_cases:
        params = {"nrb": case["nrb"], "ncellid": case["ncellid"],
                  "ports": case["ports"], "cfi": case["cfi"], "index_base": 1}
        result = execute(case["entry"], **params)
        assert result["indices"] == case["indices"]
        assert result["count"] == len(case["indices"])
        zero_based = execute(case["entry"], **(params | {"index_base": 0}))
        assert np.array_equal(np.asarray(zero_based["indices"]),
                              np.asarray(case["indices"])-1)
    for entry in ("ltePDCCHIndices", "ltePHICHIndices"):
        try:
            execute(entry, nrb=15)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{entry} must reject unsupported resource geometry")

    drs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sidelink_drs.json").read_text(encoding="utf-8"))
    for case in drs_cases:
        cfg = case["config"]
        params = {}
        for source, target in (("NSLID", "nslid"), ("NSLRB", "nrb"),
                               ("PRBSet", "prb_set"), ("SidelinkMode", "sidelink_mode"),
                               ("CyclicPrefixSL", "cyclic_prefix"),
                               ("NSAID", "nsaid"), ("NXID", "nxid"),
                               ("NSubframePSSCH", "nsubframe_pssch")):
            if source in cfg:
                params[target] = cfg[source]
        result = execute(case["entry"], **params)
        actual = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape and (not len(expected) or
                                                    np.max(abs(actual-expected)) < 1e-12)
        assert result["count"] == len(expected) and result["info"] == case["info"]
    try:
        execute("ltePSSCHDRS", nrb=25)
    except ValueError:
        pass
    else:
        raise AssertionError("ltePSSCHDRS must reject an unverified parameter set")

    preset_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_presets.json").read_text(encoding="utf-8"))
    assert len(preset_cases["records"]) == 288
    for case in preset_cases["records"]:
        kwargs = {"duplex_mode": case["duplex"]}
        if case["entry"] == "lteTestModel":
            kwargs["tmn"] = case["name"]
            kwargs["bandwidth"] = case["bandwidth"]
            kwargs["ncellid"] = case["ncellid"]
        else:
            kwargs["rc"] = case["name"]
        assert execute(case["entry"], **kwargs)["config"] == case["config"]
    for entry, kwargs in (("lteRMCDL", {"rc": "R.15"}),
                          ("lteRMCUL", {"rc": "A0-0"}),
                          ("lteTestModel", {"tmn": "1.2", "bandwidth": "9RB"})):
        try:
            execute(entry, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{entry} must reject an invalid preset")

    reference_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_reference_signals.json").read_text(encoding="utf-8"))
    assert len(reference_cases) == 135
    for case in reference_cases:
        params = {"nrb": case["nrb"], "ncellid": case["ncellid"],
                  "nsubframe": case["nsubframe"]}
        if case["entry"] == "lteCSIRS":
            params["csi_ref_ports"] = case["csi_ref_ports"]
        symbols = execute(case["entry"], **params)["symbols"]
        actual = np.asarray(symbols["real"]) + 1j*np.asarray(symbols["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape and np.max(abs(actual-expected)) < 1e-12
        positions = execute(case["entry"]+"Indices", index_base=1, **params)["indices"]
        assert positions == case["indices"]
        zero_based = execute(case["entry"]+"Indices", index_base=0, **params)["indices"]
        assert np.array_equal(np.asarray(zero_based), np.asarray(case["indices"])-1)
    for entry in ("lteCSIRS", "lteCSIRSIndices", "ltePRS", "ltePRSIndices"):
        try:
            execute(entry, ncellid=1)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{entry} must reject unverified cell configurations")

    pucch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pucch_indices.json").read_text(encoding="utf-8"))
    assert len(pucch_cases) == 432
    for case in pucch_cases:
        params = {"nrb": case["nrb"], "ncellid": case["ncellid"],
                  "nsubframe": case["nsubframe"],
                  "cyclic_prefix": case["cyclic_prefix"],
                  "resource_idx": case["resource_idx"]}
        result = execute(case["entry"], index_base=1, **params)
        assert result["indices"] == case["indices"]
        assert result["count"] == len(case["indices"])
        zero_based = execute(case["entry"], index_base=0, **params)["indices"]
        assert np.array_equal(np.asarray(zero_based), np.asarray(case["indices"])-1)
    try:
        execute("ltePUCCH3Indices", resource_idx=99)
    except ValueError:
        pass
    else:
        raise AssertionError("PUCCH indexing must reject an unverified ResourceIdx")

    pucch_drs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pucch_drs.json").read_text(encoding="utf-8"))
    assert len(pucch_drs_cases) == 288
    for case in pucch_drs_cases:
        params = {"nrb": case["nrb"], "ncellid": case["ncellid"],
                  "nsubframe": case["nsubframe"],
                  "cyclic_prefix": case["cyclic_prefix"],
                  "resource_idx": case["resource_idx"]}
        if case["entry"] == "ltePUCCH2DRS":
            params["ack"] = case["ack"]
        result = execute(case["entry"], **params)
        actual = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape and (not len(expected) or
                                                    np.max(abs(actual-expected)) < 1e-12)
        assert result["info"] == case["info"] and result["count"] == len(expected)
    try:
        execute("ltePUCCH2DRS", ack=[0, 0])
    except ValueError:
        pass
    else:
        raise AssertionError("PUCCH2DRS must reject an unverified ACK pair")

    ul_control_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_ul_control_codes.json").read_text(encoding="utf-8"))
    assert len(ul_control_cases) == 105
    for case in ul_control_cases:
        name, n = case["entry"], case["n"]
        params = {"qd": case["qd"], "modulation": case["modulation"]}
        for trial in case["trials"]:
            bits = np.atleast_1d(trial["bits"]).astype(int).tolist()
            coded = execute(name+"Encode", bits=bits, **params)["coded_bits"]
            assert coded == trial["coded"], (name, n, params)
            soft = np.where(np.asarray(coded) >= 0, 2*np.asarray(coded)-1, 0)
            decoded = execute(name+"Decode", soft_bits=soft.tolist(), length=n,
                              **params)["bits"]
            assert decoded == np.atleast_1d(trial["decoded"]).astype(int).tolist()
            if n >= 2 or name == "lteCQI":
                noisy = execute(name+"Decode", soft_bits=trial["noisy_soft"],
                                length=n, **params)["bits"]
                assert noisy == np.atleast_1d(trial["noisy_decoded"]).astype(int).tolist()
            elif any(0 < abs(value) < .5 for value in trial["noisy_soft"]):
                try:
                    execute(name+"Decode", soft_bits=trial["noisy_soft"],
                            length=n, **params)
                except ValueError:
                    pass
                else:
                    raise AssertionError("one-bit ACK/RI must reject ambiguous DTX soft inputs")
    for entry in ("lteACKEncode", "lteRIEncode", "lteCQIEncode"):
        try:
            execute(entry, bits=[0, 1], qd=3)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{entry} must reject an unsupported Qd")

    dmrs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_dmrs.json").read_text(encoding="utf-8"))
    assert len(dmrs_cases) == 96
    for case in dmrs_cases:
        params = {"nrb": case["nrb"], "ncellid": case["ncellid"],
                  "nsubframe": case["nsubframe"], "prb_set": case["prb_set"]}
        if case["entry"] == "lteDMRS":
            params["rnti"] = case["rnti"]
        else:
            params["epdcch_nid"] = case["epdcch_nid"]
        symbols = execute(case["entry"], **params)["symbols"]
        actual = np.asarray(symbols["real"]) + 1j*np.asarray(symbols["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape and np.max(abs(actual-expected)) < 1e-12
        positions = execute(case["entry"]+"Indices", index_base=1, **params)["indices"]
        assert positions == case["indices"]
        zero_based = execute(case["entry"]+"Indices", index_base=0, **params)["indices"]
        assert np.array_equal(np.asarray(zero_based), np.asarray(case["indices"])-1)
    for entry in ("lteDMRS", "lteDMRSIndices", "lteEPDCCHDMRS", "lteEPDCCHDMRSIndices"):
        try:
            execute(entry, prb_set=[4])
        except ValueError:
            pass
        else:
            raise AssertionError(f"{entry} must reject unverified PRBSet")

    epdcch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_epdcch_indices.json").read_text(encoding="utf-8"))
    assert len(epdcch_cases["records"]) == 144 and not epdcch_cases["errors"]
    for case in epdcch_cases["records"]:
        params = {"nrb": case["nrb"], "ncellid": case["ncellid"],
                  "nsubframe": case["nsubframe"], "prb_set": case["prb_set"],
                  "cfi": case["cfi"], "epdcch_type": case["epdcch_type"]}
        result = execute("lteEPDCCHIndices", index_base=1, **params)
        assert result["indices"] == case["indices"] and result["info"] == case["info"]
        assert result["count"] == len(case["indices"])
        zero_based = execute("lteEPDCCHIndices", index_base=0, **params)["indices"]
        assert np.array_equal(np.asarray(zero_based), np.asarray(case["indices"])-1)
    try:
        execute("lteEPDCCHIndices", epdcch_nid=37)
    except ValueError:
        pass
    else:
        raise AssertionError("EPDCCH data indexing must reject unverified NID")

    npusch_drs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_npusch_drs.json").read_text(encoding="utf-8"))
    assert len(npusch_drs_cases) == 24
    for case in npusch_drs_cases:
        spacing = float(case["spacing"].replace("kHz", ""))
        result = execute("lteNPUSCHDRS", spacing_khz=spacing,
                         subcarrier_set=case["subcarriers"],
                         nncellid=case["ncellid"], nslot=case["slot"],
                         nul_slots=case["nul_slots"])
        actual = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected = np.atleast_1d(case["real"]) + 1j*np.atleast_1d(case["imag"])
        assert actual.shape == expected.shape and np.max(abs(actual-expected)) < 1e-12
        assert result["state"] == case["state"] and result["count"] == len(expected)
    try:
        execute("lteNPUSCHDRS", npusch_format="Control")
    except ValueError:
        pass
    else:
        raise AssertionError("NPUSCH DRS must reject unverified Control format")

    golden = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_expansion.json").read_text(encoding="utf-8"))
    for cfi, word in golden["cfi_words"].items():
        actual = execute("lteCFI", cfi=int(cfi))["coded_bits"]
        assert "".join(map(str, actual)) == word
        assert execute("lteCFIDecode", bits=actual)["cfi"] == int(cfi)
    cfi_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_cfi_decode.json").read_text(encoding="utf-8"))
    for case in cfi_cases:
        assert execute("lteCFIDecode", soft_bits=case["soft"])["cfi"] == case["decoded"]
    assert "".join(map(str, execute("ltePBCHPRBS", cinit=12, length=32)["bits"])) == (
        golden["pbch_prbs_ncellid_12_length_32"])
    prbs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_control_prbs.json").read_text(encoding="utf-8"))
    for case in prbs_cases:
        name = case["entry"]
        params = {"ncellid": case["ncellid"], "nsubframe": case["nsubframe"]}
        if name == "lteEPDCCHPRBS":
            params["epdcch_nid"] = case["ncellid"]
        result = execute(name, **params, length=32)
        assert result["cinit"] == case["cinit"] and result["bits"] == case["bits"]
        if case["window"]:
            assert execute(name, **params, window=[7, 19])["bits"] == case["window"]
            assert execute(name, **params, length=12, mapping="signed")["bits"] == case["signed"]
    remaining_prbs = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_remaining_prbs.json").read_text(encoding="utf-8"))
    for case in remaining_prbs:
        cfg = case["config"]
        params = {}
        for source, target in (("NSLID", "nslid"), ("NSAID", "nsaid"),
                               ("NXID", "nxid"), ("NSubframePSSCH", "nsubframe_pssch"),
                               ("SidelinkMode", "sidelink_mode"),
                               ("NCellID", "ncellid"), ("NSubframe", "nsubframe"),
                               ("RNTI", "rnti")):
            if source in cfg:
                params[target] = cfg[source]
        result = execute(case["entry"], **params, length=32)
        assert result["cinit"] == case["cinit"] and result["bits"] == case["bits"]
        assert execute(case["entry"], **params, length=12,
                       mapping="signed")["bits"] == case["signed"]
    srs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_srs_info.json").read_text(encoding="utf-8"))
    for case in srs_cases:
        for subframe in range(10):
            info = execute("lteSRSInfo", subframe_config=case["config"],
                           duplex_mode=case["mode"], nsubframe=subframe)["info"]
            assert info == {"CellPeriod": case["period"], "CellOffset": case["offset"],
                            "IsSRSSubframe": case["scheduled"][subframe]}
    pcfich_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pcfich.json").read_text(encoding="utf-8"))
    phich_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_phich_info.json").read_text(encoding="utf-8"))
    for case in phich_cases:
        info = execute("ltePHICHInfo", nrb=case["nrb"], ng=case["ng"],
                       cyclic_prefix=case["cyclic_prefix"],
                       phich_duration=case["phich_duration"])["info"]
        assert info == case["info"]
    pdcch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pdcch_info.json").read_text(encoding="utf-8"))
    for case in pdcch_cases:
        info = execute("ltePDCCHInfo", nrb=case["nrb"], ng=case["ng"],
                       cyclic_prefix=case["cyclic_prefix"], ports=case["ports"],
                       cfi=case["cfi"])["info"]
        assert info == case["info"]
    interleave_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pdcch_interleave.json").read_text(encoding="utf-8"))
    for case in interleave_cases:
        source = list(range(1, 4*case["reg"]+1))
        forward = execute("ltePDCCHInterleave", symbols=source,
                          ncellid=case["ncellid"])["symbols"]
        assert forward == case["forward"]
        inverse = execute("ltePDCCHDeinterleave", symbols=forward,
                          ncellid=case["ncellid"])["symbols"]
        assert inverse == source
    dlsch_info_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_dlsch_info.json").read_text(encoding="utf-8"))
    for case in dlsch_info_cases:
        assert execute("lteDLSCHInfo", block_length=case["block_length"])["info"] == case["info"]
    sci_info_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sci_info.json").read_text(encoding="utf-8"))
    for case in sci_info_cases:
        assert execute("lteSCIInfo", nrb=case["nrb"])["info"] == case["info"]
    dci_coding_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_dci_coding.json").read_text(encoding="utf-8"))
    for case in dci_coding_cases:
        result = execute("lteDCIEncode", bits=case["bits"],
                         pdcch_format=case["format"], rnti=case["rnti"])
        assert result["coded_bits"] == case["coded"] and result["mcrc"] == case["mcrc"]
        decoded = execute("lteDCIDecode", soft_bits=[2*b-1 for b in case["coded"]],
                          payload_length=len(case["bits"]), rnti=case["rnti"])
        assert decoded["bits"] == case["bits"] and decoded["crc_rnti"] == case["crc_rnti"]
        assert decoded["mcrc"] == case["mcrc"] and decoded["crc_ok"]
    dci_info_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_dci_info.json").read_text(encoding="utf-8"))
    for case in dci_info_cases:
        info = execute("lteDCIInfo", nrb=case["nrb"],
                       ports=case["ports"], duplex_mode=case["mode"])["info"]
        assert info == case["info"]
    bch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_bch.json").read_text(encoding="utf-8"))
    for case in bch_cases:
        coded = execute("lteBCH", bits=case["bits"],
                        cyclic_prefix=case["cp"], ports=case["ports"])["coded_bits"]
        assert coded == case["coded"]
        decoded = execute("lteBCHDecode", soft_bits=[2*b-1 for b in coded])["bits"]
        assert decoded == case["bits"]
        assert execute("lteBCHDecode", soft_bits=[2*b-1 for b in coded])["cell_ref_ports"] == case["detected"]
        if case["ports"] == 1:
            symbols = execute("ltePBCH", bits=coded, ncellid=37)["symbols"]
            actual = np.asarray(symbols["real"]) + 1j*np.asarray(symbols["imag"])
            expected = np.asarray(case["pbch_real"]) + 1j*np.asarray(case["pbch_imag"])
            assert np.max(abs(actual-expected)) < 1e-12
            result = execute("ltePBCHDecode", symbols=symbols, ncellid=37)
            assert result["trblk"] == case["bits"] and result["cell_ref_ports"] == 1
            assert np.max(abs(np.asarray(result["soft_bits"])-np.asarray(case["pbch_soft"]))) < 1e-12
    slbch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_slbch.json").read_text(encoding="utf-8"))
    for case in slbch_cases:
        cfg = case["config"]
        params = {"sidelink_mode": cfg["SidelinkMode"],
                  "cyclic_prefix": cfg["CyclicPrefixSL"]}
        coded = execute("lteSLBCH", bits=case["bits"], **params)["coded_bits"]
        assert coded == case["coded"]
        decoded = execute("lteSLBCHDecode", soft_bits=[2*b-1 for b in coded],
                          **params)
        assert decoded["bits"] == case["bits"] and not decoded["crc_error"]
    prach_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_prach_info.json").read_text(encoding="utf-8"))
    for case in prach_cases:
        assert execute("ltePRACHInfo", nrb=case["nrb"],
                       preamble_format=case["format"])["info"] == case["info"]
    nprach_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_nprach_info.json").read_text(encoding="utf-8"))
    for case in nprach_cases:
        spacing = float(case["spacing"].replace("kHz", ""))
        assert execute("lteNPRACHInfo", nncellid=case["cellid"],
                       spacing_khz=spacing, nprach_format=case["format"])["info"] == case["info"]
    ulsch_interleave_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_ulsch_interleave.json").read_text(encoding="utf-8"))
    for case in ulsch_interleave_cases:
        params = {"cyclic_prefix": case["cp"], "shortened": case["shortened"],
                  "modulation": case["modulation"]}
        forward = execute("lteULSCHInterleave", bits=case["data"], **params)["bits"]
        assert forward == case["interleaved"]
        inverse = execute("lteULSCHDeinterleave", bits=forward, **params)["bits"]
        assert inverse == case["data"]
    sci_coding_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sci_coding.json").read_text(encoding="utf-8"))
    for case in sci_coding_cases:
        cfg = case["config"]
        params = {"nrb": cfg["NSLRB"], "sidelink_mode": cfg["SidelinkMode"],
                  "cyclic_prefix": cfg["CyclicPrefixSL"]}
        coded = execute("lteSCIEncode", bits=case["bits"], **params)
        assert coded["coded_bits"] == case["coded"] and coded["mcrc"] == case["mcrc"]
        decoded = execute("lteSCIDecode", soft_bits=[2*b-1 for b in case["coded"]],
                          payload_length=len(case["bits"]), **params)
        assert decoded["bits"] == case["bits"] and not decoded["crc_error"]
        assert decoded["mcrc"] == case["mcrc"]
    sl_scfdma_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sl_scfdma.json").read_text(encoding="utf-8"))
    for case in sl_scfdma_cases:
        params = {"nrb": case["nrb"], "cyclic_prefix": case["cp"]}
        assert execute("lteSLSCFDMAInfo", **params)["info"] == case["info"]
        assert execute("lteSLSCFDMAInfo", windowing=0, **params)["info"] == case["modinfo"]
    codebook_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pusch_codebook.json").read_text(encoding="utf-8"))
    for case in codebook_cases:
        antennas, layers, pmi = case["antennas"], case["layers"], case["pmi"]
        info = execute("lteULPMIInfo", nrb=25, n_tx_ants=antennas,
                       n_layers=layers)["info"]
        assert info == {"k": 25, "NSubbands": 1, "MaxPMI": case["max_pmi"]}
        identity = np.eye(layers)
        pre = execute("ltePUSCHPrecode", symbols=identity.tolist(),
                      n_tx_ants=antennas, n_layers=layers, pmi=pmi)["symbols"]
        matrix = np.asarray(pre["real"]) + 1j*np.asarray(pre["imag"])
        expected = np.asarray(case["matrix_real"]).reshape(layers, antennas) + 1j*np.asarray(case["matrix_imag"]).reshape(layers, antennas)
        assert matrix.shape == expected.shape and np.max(abs(matrix-expected)) < 1e-12
        de = execute("ltePUSCHDeprecode", symbols=pre, n_tx_ants=antennas,
                     n_layers=layers, pmi=pmi)["symbols"]
        restored = np.asarray(de["real"]) + 1j*np.asarray(de["imag"])
        assert np.max(abs(restored-identity)) < 1e-12
    sidelink_channel_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sidelink_channels.json").read_text(encoding="utf-8"))
    for case in sidelink_channel_cases:
        cfg = case["config"]
        params = {"bits": case["bits"]}
        for source, target in (("NSLID", "nslid"), ("NSAID", "nsaid"),
                               ("NXID", "nxid"), ("NSubframePSSCH", "nsubframe_pssch"),
                               ("SidelinkMode", "sidelink_mode"),
                               ("CyclicPrefixSL", "cyclic_prefix"),
                               ("Modulation", "modulation")):
            if source in cfg:
                params[target] = cfg[source]
        actual = execute(case["entry"], **params)["symbols"]
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        values = np.asarray(actual["real"]) + 1j*np.asarray(actual["imag"])
        assert values.shape == expected.shape and np.max(abs(values-expected)) < 3e-12
        result = execute(case["entry"]+"Decode", symbols=actual, **{
            key: value for key, value in params.items() if key != "bits"})
        soft = np.asarray(result["soft_bits"])
        expected_soft = np.asarray(case["soft"])
        assert soft.shape == expected_soft.shape and np.max(abs(soft-expected_soft)) < 3e-12
        restored = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected_symbols = np.asarray(case["decoded_real"]) + 1j*np.asarray(case["decoded_imag"])
        assert np.max(abs(restored-expected_symbols)) < 3e-12
    assert execute("ltePCFICHInfo")["info"] == pcfich_cases["info"]
    for case in pcfich_cases["positions"]:
        positions = execute("ltePCFICHIndices", nrb=case["nrb"],
                            ncellid=case["ncellid"], ports=case["ports"],
                            index_base=1)["indices"]
        assert np.array_equal(positions, case["indices"])
    pcfich_symbols = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pcfich_symbols.json").read_text(encoding="utf-8"))
    for case in pcfich_symbols:
        params = {"ncellid": case["ncellid"], "nsubframe": case["nsubframe"], "ports": 1}
        result = execute("ltePCFICH", bits=case["coded"], **params)["symbols"]
        actual = np.asarray(result["real"]) + 1j*np.asarray(result["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape and np.max(abs(actual-expected)) < 1e-12
        soft = execute("ltePCFICHDecode", symbols=result, **params)["soft_bits"]
        assert np.max(abs(np.asarray(soft)-np.asarray(case["soft"]))) < 1e-12
    duplex_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_duplexing.json").read_text(encoding="utf-8"))
    for case in duplex_cases:
        cfg = case["config"]
        params = {"duplex_mode": cfg["DuplexMode"]}
        for source, target in (("CyclicPrefix", "cyclic_prefix"),
                               ("CyclicPrefixUL", "cyclic_prefix_ul"),
                               ("TDDConfig", "tdd_config"),
                               ("SSC", "ssc"), ("NSubframe", "nsubframe")):
            if source in cfg:
                params[target] = cfg[source]
        assert execute("lteDuplexingInfo", **params)["info"] == case["info"]
    pbch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_pbch_indices.json").read_text(encoding="utf-8"))
    for case in pbch_cases:
        cfg = case["config"]
        positions = execute("ltePBCHIndices", nrb=cfg["NDLRB"],
                            ncellid=cfg["NCellID"], ports=cfg["CellRefP"],
                            cyclic_prefix=cfg.get("CyclicPrefix", "Normal"),
                            nsubframe=cfg["NSubframe"], index_base=1)["indices"]
        assert np.array_equal(np.asarray(positions).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
    assert execute("lteDLResourceGridSize", nrb=6)["size"] == golden["dl_grid_nrb_6_ports_1"]

    assert execute("saLteNscRB")["subcarriers"] == 12
    assert execute("lteDLResourceGridSize", nrb=6)["size"] == [72, 14, 1]
    assert execute("lteULResourceGridSize", nrb=6, cyclic_prefix="Extended")["size"] == [72, 12, 1]
    assert execute("lteCFI", cfi=2)["coded_bits"] == ([1, 0, 1]*11)[:32]
    assert execute("lteCFIDecode", bits=([1, 0, 1]*11)[:32])["cfi"] == 2
    ack = execute("lteACKEncode", bits=[0, 1], length=8)["coded_bits"]
    assert execute("lteACKDecode", bits=ack, length=2)["bits"] == [0, 1]
    dci = execute("lteDCIEncode", bits=[0, 1]*8, mask=17)["coded_bits"]
    decoded = execute("lteDCIDecode", bits=dci, mask=17)
    assert decoded["crc_ok"] and decoded["bits"] == [0, 1]*8
    permuted = execute("ltePDCCHInterleave", bits=[0, 1, 1, 0, 1, 0, 0, 1])["bits"]
    assert execute("ltePDCCHDeinterleave", bits=permuted)["bits"] == [0, 1, 1, 0, 1, 0, 0, 1]
    q = execute("ltePDSCH", bits=[0, 1, 1, 0], cinit=12)["symbols"]
    recovered = execute("ltePDSCHDecode", symbols=q, cinit=12)["bits"]
    assert recovered == [0, 1, 1, 0]
    assert execute("ltePBCHPRBS", length=32, cinit=11)["bits"] == execute(
        "ltePDCCHPRBS", length=32, cinit=11)["bits"]
    indices = execute("ltePBCHIndices", nrb=6, ncellid=0, ports=1,
                      index_base=1)["indices"]
    assert len(indices) == 240 and indices[0] == [2, 8, 1]
    tx = execute("lte3DChannel", waveform={"real": [1, 0, 0], "imag": [0, 0, 0]},
                 taps={"real": [1, .5], "imag": [0, 0]})["waveform"]
    assert np.allclose(tx["real"], [1, .5, 0])
    assert execute("lteThroughputAnalyzer", transport_blocks=[100, 200],
                   elapsed_seconds=2)["throughput_bps"] == 1200
    assert execute("lteDLSCHInfo", block_length=1000)["segmentation"]["C"] == 1
    assert execute("lteDCIInfo", fields={"A": [1, 0], "B": [1]})["bit_length"] == 3
    assert execute("lteDuplexingInfo", duplex_mode="TDD", tdd_config=0,
                   nsubframe=2)["subframe_type"] == "Uplink"
    mib_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_mib.json").read_text(encoding="utf-8"))
    for case in mib_cases:
        result = execute("lteMIB", fields=case["config"])
        assert result["bits"] == case["bits"]
        assert execute("lteMIB", bits=case["bits"])["fields"] == case["decoded"]
    sl_mib_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sl_mib.json").read_text(encoding="utf-8"))
    for case in sl_mib_cases:
        result = execute("lteSLMIB", fields=case["config"])
        assert result["bits"] == case["bits"]
        assert execute("lteSLMIB", bits=case["bits"])["fields"] == case["decoded"]
    psss_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_psss.json").read_text(encoding="utf-8"))
    for case in psss_cases:
        if case["kind"] == "sequence":
            result = execute("ltePSSS", nslid=case["nslid"])["symbols"]
            actual = np.asarray(result["real"]) + 1j*np.asarray(result["imag"])
            expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
            assert actual.shape == expected.shape and np.max(abs(actual-expected)) < 3e-12
        else:
            positions = execute("ltePSSSIndices", nrb=case["nrb"],
                                cyclic_prefix=case["cyclic_prefix"], index_base=1)["indices"]
            assert np.array_equal(positions, case["indices"])
    ssss_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_ssss.json").read_text(encoding="utf-8"))
    for case in ssss_cases:
        result = execute("lteSSSS", nslid=case["nslid"],
                         sidelink_mode=case["mode"])
        symbols = result["symbols"]
        assert result["count"] == 124
        assert symbols["real"] == case["real"]
        assert symbols["imag"] == [0]*124
    for mode in ("D2D", "V2X"):
        for nslid in range(336):
            symbols = execute("lteSSSS", nslid=nslid,
                              sidelink_mode=mode)["symbols"]
            assert symbols["real"][:62] == symbols["real"][62:]
            assert set(symbols["real"]) <= {-1, 1}
    psbch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_psbch_indices.json").read_text(encoding="utf-8"))
    for case in psbch_cases:
        positions = execute("ltePSBCHIndices", nrb=case["nrb"],
                            sidelink_mode=case["mode"],
                            cyclic_prefix=case["cyclic_prefix"], index_base=1)["indices"]
        assert np.array_equal(positions, case["indices"])
    psbch_drs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_psbch_drs_indices.json").read_text(encoding="utf-8"))
    for case in psbch_drs_cases:
        positions = execute("ltePSBCHDRSIndices", nrb=case["nrb"],
                            sidelink_mode=case["mode"],
                            cyclic_prefix=case["cyclic_prefix"], index_base=1)["indices"]
        assert np.array_equal(positions, case["indices"])
    sidelink_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_sidelink_indices.json").read_text(encoding="utf-8"))
    for case in sidelink_cases:
        cfg = case["config"]
        params = {"nrb": cfg["NSLRB"], "cyclic_prefix": cfg.get("CyclicPrefixSL", "Normal"),
                  "index_base": 1}
        if case["entry"] != "lteSSSSIndices":
            params.update(prb_set=cfg["PRBSet"], sidelink_mode=cfg["SidelinkMode"])
            if "Modulation" in cfg:
                params["modulation"] = cfg["Modulation"]
        result = execute(case["entry"], **params)
        assert np.array_equal(np.asarray(result["indices"]).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
        if "info" in case:
            assert result["info"] == case["info"]
    grid_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_grid_sizes.json").read_text(encoding="utf-8"))
    for case in grid_cases:
        params = {"nrb": case["nrb"], "cyclic_prefix": case["cyclic_prefix"],
                  "ports": case["ports"]}
        for suffix in ("ResourceGrid", "ResourceGridSize"):
            result = execute(f"lte{case['link']}{suffix}", **params)
            assert result["size"] == case["shape"] == case["grid_shape"]
            assert result["grid"]["fill_real"] == 0 and case["all_zero"]
    nb_grid_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_nb_grid.json").read_text(encoding="utf-8"))
    for case in nb_grid_cases:
        cfg = case["config"]
        params = ({"nb_ref_ports": cfg["NBRefP"]} if "NBRefP" in cfg else
                  {"link": "uplink", "spacing_khz": float(cfg["NBULSubcarrierSpacing"].lower().replace("khz", ""))})
        assert execute("lteNBResourceGrid", **params)["size"] == case["shape"]
    npbch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_npbch_indices.json").read_text(encoding="utf-8"))
    for case in npbch_cases:
        cfg = case["config"]
        result = execute("lteNPBCHIndices", nncellid=cfg["NNCellID"],
                         nb_ref_ports=cfg["NBRefP"], nsubframe=cfg["NSubframe"],
                         nframe=cfg["NFrame"], index_base=1)
        assert np.array_equal(np.asarray(result["indices"]).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
        assert result["info"] == case["info"]
    drs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_npusch_drs_indices.json").read_text(encoding="utf-8"))
    for case in drs_cases:
        ue, channel = case["ue"], case["channel"]
        params = {"spacing_khz": float(ue["NBULSubcarrierSpacing"].lower().replace("khz", "")),
                  "npusch_format": channel["NPUSCHFormat"],
                  "subcarrier_set": channel["NBULSubcarrierSet"], "index_base": 1}
        positions = execute("lteNPUSCHDRSIndices", **params)["indices"]
        assert np.array_equal(np.asarray(positions).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
    npusch_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_npusch_indices.json").read_text(encoding="utf-8"))
    for case in npusch_cases:
        ue, channel = case["ue"], case["channel"]
        params = {"spacing_khz": float(ue["NBULSubcarrierSpacing"].lower().replace("khz", "")),
                  "npusch_format": channel["NPUSCHFormat"],
                  "subcarrier_set": channel["NBULSubcarrierSet"],
                  "nru": channel["NRU"], "nul_slots": channel["NULSlots"],
                  "modulation": channel["Modulation"], "index_base": 1}
        result = execute("lteNPUSCHIndices", **params)
        assert np.array_equal(np.asarray(result["indices"]).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
        assert result["info"] == case["info"]
    nb_downlink_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_nb_downlink_indices.json").read_text(encoding="utf-8"))
    for case in nb_downlink_cases:
        enb, channel = case["enb"], case["channel"]
        params = {"nncellid": enb["NNCellID"], "nb_ref_ports": enb["NBRefP"],
                  "operation_mode": enb.get("OperationMode", "Standalone"),
                  "control_region_size": enb.get("ControlRegionSize", 3),
                  "index_base": 1}
        if "CellRefP" in enb:
            params["cell_ref_ports"] = enb["CellRefP"]
        if case["entry"] == "lteNPDSCHIndices":
            params.update(data_type=channel["NPDSCHDataType"], nsf=channel["NSF"],
                          modulation=channel["Modulation"])
        else:
            params["ncce"] = channel["NCCE"]
        result = execute(case["entry"], **params)
        assert np.array_equal(np.asarray(result["indices"]).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
        assert result["info"] == case["info"]
    nsss_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_nsss.json").read_text(encoding="utf-8"))
    for case in nsss_cases:
        cfg = case["config"]
        params = {"nncellid": cfg["NNCellID"], "nsubframe": cfg["NSubframe"],
                  "nframe": cfg["NFrame"], "operation_mode": cfg["OperationMode"]}
        if "NCellID" in cfg:
            params.update(ncellid=cfg["NCellID"], cell_ref_ports=cfg["CellRefP"])
        result = execute("lteNSSS", **params)
        actual = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape
        if actual.size:
            assert np.max(abs(actual-expected)) < 1e-12
        positions = execute("lteNSSSIndices", **params, index_base=1)["indices"]
        assert np.array_equal(np.asarray(positions).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
    npss_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_npss.json").read_text(encoding="utf-8"))
    for case in npss_cases:
        cfg = case["config"]
        params = {"nsubframe": cfg["NSubframe"], "operation_mode": cfg["OperationMode"]}
        if "NCellID" in cfg:
            params.update(ncellid=cfg["NCellID"], cell_ref_ports=cfg["CellRefP"])
        result = execute("lteNPSS", **params)
        actual = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape
        if actual.size:
            assert np.max(abs(actual-expected)) < 1e-12
        positions = execute("lteNPSSIndices", **params, index_base=1)["indices"]
        assert np.array_equal(np.asarray(positions).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
    nrs_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_nrs.json").read_text(encoding="utf-8"))
    for case in nrs_cases:
        cfg = case["config"]
        params = {"nncellid": cfg["NNCellID"], "nsubframe": cfg["NSubframe"],
                  "nb_ref_ports": cfg["NBRefP"]}
        result = execute("lteNRS", **params)
        actual = np.asarray(result["symbols"]["real"]) + 1j*np.asarray(result["symbols"]["imag"])
        expected = np.asarray(case["real"]) + 1j*np.asarray(case["imag"])
        assert actual.shape == expected.shape and np.max(abs(actual-expected)) < 1e-12
        positions = execute("lteNRSIndices", **params, index_base=1)["indices"]
        assert np.array_equal(np.asarray(positions).reshape(-1, 3),
                              np.asarray(case["indices"]).reshape(-1, 3))
    turbo_cases = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_turbo.json").read_text(encoding="utf-8"))
    for case in turbo_cases:
        result = execute("lteTurboEncode", bits=case["bits"])["coded_bits"]
        assert result == case["coded"]
        if "soft" in case:
            decoded = execute("lteTurboDecode", soft_bits=case["soft"])["bits"]
            assert decoded == case["decoded"]
        if "rate_match" in case:
            for version, golden_bits in case["rate_match"].items():
                rv = int(version[-1])
                assert execute("lteRateMatchTurbo", bits=case["coded"],
                               length=len(golden_bits), rv=rv)["bits"] == golden_bits
                restored = execute("lteRateRecoverTurbo",
                                   soft_bits=2*np.asarray(golden_bits)-1,
                                   block_size=len(case["bits"]), rv=rv)["soft_bits"]
                assert np.array_equal(restored, case["rate_recover"][version])
    print(f"PASS {len(names)} new LTE public entries and representative numerical invariants")


if __name__ == "__main__":
    main()
