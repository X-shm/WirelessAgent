"""Exercise each newly mapped 5G entry through the public MCP adapter."""

from __future__ import annotations

import json
import sys
import unittest

import numpy as np
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

from mcp_server.catalog import ROOT, load_catalog
from mcp_server.server import create_server


sys.path.insert(0, str(ROOT / "tools"))

from _nr_remaining_common import json_ready
from nr_bch_codec import bch
from nr_control_codec import uci_encode
from nr_dci import dci_encode
from nr_prach_family import prach
from nr_pucch_family import pucch
from nr_sch_transport import ulsch
from nr_waveform_io import waveform_generator


GROUPS = (
    "nr_bch_codec", "nr_channel_models", "nr_control_codec", "nr_csi_resources",
    "nr_pdcch_resources", "nr_prach_family", "nr_ptrs_family",
    "nr_pucch_family", "nr_sch_transport", "nr_waveform_io",
)


def entry_cases() -> dict[str, tuple[str, dict]]:
    """Small, valid, deterministic inputs for all 45 dispatch branches."""
    payload = (np.arange(12) % 2).astype(np.uint8)
    mib = (np.arange(24) % 2).astype(np.uint8)
    bch_bits = bch(mib, 42, 1, 4, 17, 321)["codeword"]
    uci_bits = uci_encode(payload, 108)["codeword"]
    dci_bits = dci_encode(payload, 23, 108)
    prach_symbols = prach(1, 139, 17)["symbols"]
    csirs_grid = np.zeros((24, 1), complex)
    csirs_grid[0, 0] = 1
    pucch_symbols = pucch(0, ack=[1], nid=7)["symbols"]
    sch_payload = (np.arange(24) % 2).astype(np.uint8)
    sch_bits = ulsch(sch_payload, .5, 672)["codeword"]
    grid = np.zeros((12, 1), complex)
    grid[3, 0] = 1 + 1j
    waveform = waveform_generator(grid, 128)["waveform"]
    llr = lambda bits, magnitude=20: ((1 - 2 * bits.astype(float)) * magnitude).tolist()
    grouped = {
        "nr_bch_codec": {
            "nrBCH": {"payload": mib.tolist(), "sfn": 42, "hrf": 1,
                      "lssb": 4, "idxoffset": 17, "ncellid": 321},
            "nrBCHDecode": {"llr": llr(bch_bits, 30), "lssb": 4, "ncellid": 321},
        },
        "nr_channel_models": {
            "nrTDLChannel": {"samples": [1, 0], "sample_rate": 1000,
                             "delays": [0, .001], "gains": [1, .5]},
            "nrCDLChannel": {"samples": [1, 0], "sample_rate": 1000,
                             "delays": [0], "gains": [1]},
            "nrHSTChannel": {"samples": [1, 0], "sample_rate": 1000,
                             "speed_mps": 0, "carrier_hz": 3.5e9},
            "nrPathLoss": {"freq_hz": 3.5e9, "bs": [0, 0, 30], "ue": [100, 0, 1.5]},
            "nrPerfectChannelEstimate": {"path_gains": [1], "delays": [0],
                                         "sample_rate": 1.92e6, "nfft": 128, "nsc": 12},
            "nrPhaseNoise": {"samples": [1, 1], "sample_rate": 1000,
                             "linewidth_hz": 0},
        },
        "nr_control_codec": {
            "nrDCIDecode": {"llr": llr(dci_bits), "payload_length": 12, "rnti": 23},
            "nrUCIEncode": {"payload": payload.tolist(), "e": 108},
            "nrUCIDecode": {"llr": llr(uci_bits), "payload_length": 12},
        },
        "nr_csi_resources": {
            "nrCSIRSIndices": {"nrb": 2, "symbol": 0, "subcarrier_offset": 0,
                               "density": 1},
            "nrCSIRSMeasurements": {"grid": json_ready(csirs_grid), "indices": [1],
                                    "nrb": 2},
            "nrCSIReportCSIRS": {"channel": [1], "noise_variance": 1},
            "nrCSIMeasurementsSRS": {"channel": [1], "noise_variance": 1},
        },
        "nr_pdcch_resources": {
            "nrPDCCHResources": {"nrb": 6},
            "nrPDCCHSpace": {"nrb": 12, "coreset_nrb": 12,
                             "num_candidates": [2, 1, 0, 0, 0]},
        },
        "nr_prach_family": {
            "nrPRACH": {"root": 1, "sequence_length": 139, "cyclic_shift": 17},
            "nrPRACHDetect": {"received": json_ready(prach_symbols), "root": 1,
                              "sequence_length": 139},
            "nrPRACHGrid": {"sequence_length": 139,
                            "symbols": json_ready(prach_symbols)},
            "nrPRACHIndices": {"sequence_length": 139},
            "nrPRACHOFDMInfo": {"sequence_length": 139},
            "nrPRACHOFDMModulate": {"symbols": json_ready(prach_symbols),
                                   "nfft": 256},
        },
        "nr_ptrs_family": {
            "nrPDSCHPTRS": {"nrb": 8, "rb_set": list(range(8)), "nid": 17},
            "nrPDSCHPTRSIndices": {"nrb": 8, "rb_set": list(range(8))},
            "nrPUSCHPTRS": {"nrb": 8, "rb_set": list(range(8)), "nid": 17},
            "nrPUSCHPTRSIndices": {"nrb": 8, "rb_set": list(range(8))},
        },
        "nr_pucch_family": {
            "nrPUCCH": {"format_number": 0, "ack": [1], "nid": 7},
            "nrPUCCH0": {"ack": [1], "nid": 7},
            "nrPUCCH1": {"uci_bits": [0, 1], "nid": 7},
            "nrPUCCH2": {"uci_bits": [0, 1] * 4, "nid": 7},
            "nrPUCCH3": {"uci_bits": [0, 1] * 4, "nid": 7},
            "nrPUCCH4": {"uci_bits": [0, 1] * 4, "nid": 7},
            "nrPUCCHDecode": {"symbols": json_ready(pucch_symbols),
                              "format_number": 0, "nid": 7, "ack_bits": 1},
            "nrPUCCHDMRS": {"nid": 7, "format_number": 2, "num_symbols": 2},
            "nrPUCCHDMRSIndices": {"nrb": 1, "format_number": 2, "num_symbols": 2},
            "nrPUCCHHoppingInfo": {"nid": 7},
            "nrPUCCHIndices": {"nrb": 1, "format_number": 2, "num_symbols": 2},
        },
        "nr_sch_transport": {
            "nrDLSCHDecoder": {"llr": llr(sch_bits), "tbs": 24,
                                  "target_code_rate": .5},
            "nrULSCH": {"payload": sch_payload.tolist(), "target_code_rate": .5,
                        "e": 672},
            "nrULSCHDecoder": {"llr": llr(sch_bits), "tbs": 24,
                                  "target_code_rate": .5},
            "nrULSCHDemultiplex": {"codeword": [1, 0, 0, 1, 1],
                                   "uci_positions": [1, 3]},
            "nrULSCHMultiplex": {"data_bits": [1, 0, 1], "uci_bits": [0, 1],
                                 "uci_positions": [1, 3], "total_length": 5},
        },
        "nr_waveform_io": {
            "nrWaveformAnalyzer": {"waveform": json_ready(waveform), "nfft": 128,
                                   "nrb": 1, "symbols": 1},
            "nrWaveformGenerator": {"grid": json_ready(grid), "nfft": 128},
        },
    }
    assert set(grouped) == set(GROUPS)
    return {name: (group, params) for group, entries in grouped.items()
            for name, params in entries.items()}


class RemainingNRMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_process_exposes_new_5g_groups(self) -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server", "--tools", ",".join(GROUPS)],
            cwd=str(ROOT),
        )
        async with Client(params) as client:
            listed = {tool.name for tool in (await client.list_tools()).tools}
            self.assertEqual(listed, set(GROUPS))
            result = await client.call_tool(
                "nr_prach_family",
                {"function": "nrPRACHIndices", "params": '{"sequence_length":139}'},
            )
            self.assertFalse(result.is_error, str(result.content))
            self.assertEqual(len(result.structured_content["result"]["indices"]), 139)

    async def test_all_45_registered_branches_execute_over_mcp(self) -> None:
        registry = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))
        entries = {item["name"]: item for item in registry["tools"] if item["name"] in GROUPS}
        self.assertEqual(set(entries), set(GROUPS))
        cases = entry_cases()
        self.assertEqual(len(cases), 45)
        self.assertEqual(set(cases), {source for item in entries.values()
                                      for source in item["source_functions"]})
        catalog = load_catalog(set(GROUPS))
        async with Client(create_server(only=set(GROUPS)), read_timeout_seconds=60) as client:
            listed = {tool.name: tool for tool in (await client.list_tools()).tools}
            self.assertEqual(set(listed), set(GROUPS))
            for name, (group, params) in cases.items():
                with self.subTest(function=name):
                    self.assertIn(name, catalog[group].input_schema["properties"]["function"]["enum"])
                    packed = json.dumps(params, separators=(",", ":"), allow_nan=False)
                    self.assertLessEqual(len(packed), 16_000)
                    result = await client.call_tool(group, {"function": name, "params": packed})
                    self.assertFalse(result.is_error, f"{name}: {result.content}")
                    self.assertEqual(result.structured_content["function"], name)
                    self.assertIn("result", result.structured_content)

    async def test_dispatch_rejects_unknown_and_malformed_requests(self) -> None:
        async with Client(create_server(only={"nr_prach_family"})) as client:
            unknown = await client.call_tool("nr_prach_family",
                                             {"function": "nrNotAnEntry", "params": "{}"})
            self.assertTrue(unknown.is_error)
            self.assertEqual(json.loads(unknown.content[0].text)["code"], "INVALID_ARGUMENT")
            malformed = await client.call_tool("nr_prach_family",
                                               {"function": "nrPRACH", "params": "[1]"})
            self.assertTrue(malformed.is_error)
            self.assertEqual(json.loads(malformed.content[0].text)["code"], "TOOL_ERROR")

    async def test_long_standard_sequence_inputs_over_mcp(self) -> None:
        sequence = prach(1, 839, 17)["symbols"]
        prach_params = json.dumps({"received": json_ready(sequence), "root": 1,
                                   "sequence_length": 839}, separators=(",", ":"))
        self.assertGreater(len(prach_params), 16_000)
        self.assertLess(len(prach_params), 250_000)

        rng = np.random.default_rng(19)
        grid = rng.normal(size=(12, 14)) + 1j * rng.normal(size=(12, 14))
        waveform = waveform_generator(grid, 128)["waveform"]
        waveform_params = json.dumps({"waveform": json_ready(waveform), "nfft": 128,
                                      "nrb": 1, "symbols": 14}, separators=(",", ":"))
        self.assertGreater(len(waveform_params), 16_000)
        self.assertLess(len(waveform_params), 250_000)

        async with Client(create_server(only={"nr_prach_family", "nr_waveform_io"}),
                          read_timeout_seconds=60) as client:
            detected = await client.call_tool(
                "nr_prach_family", {"function": "nrPRACHDetect", "params": prach_params})
            self.assertFalse(detected.is_error, str(detected.content))
            self.assertEqual(detected.structured_content["result"]["cyclic_shift"], 17)

            analyzed = await client.call_tool(
                "nr_waveform_io",
                {"function": "nrWaveformAnalyzer", "params": waveform_params},
            )
            self.assertFalse(analyzed.is_error, str(analyzed.content))
            recovered = analyzed.structured_content["result"]["grid"]
            actual = np.asarray(recovered["real"]) + 1j * np.asarray(recovered["imag"])
            self.assertTrue(np.allclose(actual, grid, atol=1e-12))

    async def test_one_bit_pucch1_roundtrip_over_mcp(self) -> None:
        async with Client(create_server(only={"nr_pucch_family"})) as client:
            encoded = await client.call_tool(
                "nr_pucch_family",
                {"function": "nrPUCCH1", "params": '{"uci_bits":[1],"nid":7}'},
            )
            self.assertFalse(encoded.is_error, str(encoded.content))
            decoded = await client.call_tool(
                "nr_pucch_family",
                {"function": "nrPUCCHDecode", "params": json.dumps({
                    "symbols": encoded.structured_content["result"]["symbols"],
                    "format_number": 1, "nid": 7, "num_symbols": 4,
                    "uci_bits_length": 1,
                })},
            )
            self.assertFalse(decoded.is_error, str(decoded.content))
            self.assertEqual(decoded.structured_content["result"]["bits"], [1])


if __name__ == "__main__":
    unittest.main()
