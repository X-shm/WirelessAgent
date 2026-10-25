"""Exercise every newly mapped public WLAN name and core numerical invariants."""
from __future__ import annotations

import sys
import json
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import wlan_config_family as cfg
import wlan_numeric_family as numeric
import wlan_bit_routing as routing
import wlan_ofdm_family as ofdm
import wlan_receiver_family as receiver
import wlan_bit_recovery as bits
import wlan_signal_fields as fields
import wlan_mac_family as mac
import wlan_channel_waveform as channel
import wlan_constellation as constellation
from wlan_symbol_timing import lltf_waveform


def iq(values):
    array = np.asarray(values, dtype=complex)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


def main():
    checked = set()
    for name, fn in cfg.DISPATCH.items():
        result = fn(name="bcc") if name == "wlan.type.ChannelCoding" else fn()
        assert result["class"] == name
        checked.add(name)
    assert cfg.DISPATCH["wlanEHTRU"](properties={"RUSize": 242, "RUIndex": 1})["properties"]["RUSize"] == 242
    assert cfg.DISPATCH["wlanURAConfig"]()["properties"]["Size"] == [2, 2]

    numeric_cases = {
        "wlanAPEPLength": {"num_data_symbols": 10},
        "wlanChannelFrequency": {"channel": 6, "band": 2.4},
        "wlanClosestReferenceSymbol": {"symbols": iq([-0.9+0j, 0.8+0j])},
        "wlanHETBNDPFeedbackStatus": {"first_tone_set": iq([1+0j]),
                                        "second_tone_set": iq([.1+0j])},
        "wlanInterpretScramblerState": {"scram_init": 93},
        "wlanMSDULengths": {"frame_length": 3000},
        "wlanPSDULength": {"num_data_symbols": 10},
        "wlanReferenceSymbols": {"modulation": "QPSK"},
        "wlanSampleRate": {"channel_bandwidth": "CBW20"},
        "wlanSpectralFlatness": {"channel_est": iq([1+0j, 1+0j])},
    }
    for name, fn in numeric.DISPATCH.items():
        assert isinstance(fn(**numeric_cases[name]), dict)
        checked.add(name)
    assert numeric.wlan_channel_frequency(6, 2.4)["frequency_hz"] == 2437e6
    assert numeric.wlan_reference_symbols("BPSK")["symbols"]["real"] == [-1, 1]
    assert numeric.wlan_spectral_flatness(iq([1, 1]))["pass"]

    original = [i % 2 for i in range(48)]
    interleaved = routing.wlan_bcc_interleave(original, 48)["bits"]
    assert routing.wlan_bcc_deinterleave(interleaved, 48)["bits"] == original
    streams = routing.wlan_stream_parse(original, 2, 48)["streams"]
    assert routing.wlan_stream_deparse(streams, num_cbps=48)["bits"] == original
    segments = routing.wlan_segment_parse_bits(original, "CBW160")["segments"]
    assert routing.wlan_segment_deparse_bits(segments, "CBW160")["bits"] == original
    tones = list(range(8))
    split = routing.wlan_segment_parse_symbols(tones, "CBW160")["segments"]
    assert routing.wlan_segment_deparse_symbols(split, "CBW160")["symbols"] == tones
    checked.update(routing.DISPATCH)

    for name, fn in ofdm.DISPATCH.items():
        bandwidth = "CBW2160" if "DMG" in name else "CBW2" if "S1G" in name else "CBW20"
        params = {"channel_bandwidth": bandwidth}
        if name in ofdm.DEMOD:
            params.update(waveform=iq(np.ones(80)), fft_length=64, cp_length=16)
        result = fn(**params)
        assert isinstance(result, dict)
        checked.add(name)
    assert ofdm.geometry("HE", "CBW20")["fft_length"] == 256
    lltf = ofdm.DISPATCH["wlanLLTFDemodulate"](waveform=iq(lltf_waveform("CBW20")))
    assert lltf["num_symbols"] == 2 and lltf["cp_length"] == 32
    lltf_grid = np.asarray(lltf["symbols"]["real"]) + 1j * np.asarray(lltf["symbols"]["imag"])
    assert lltf_grid.shape == (64, 2, 1) and np.max(abs(lltf_grid[:, 0] - lltf_grid[:, 1])) < 1e-12

    received = iq([[2+0j, 2+0j], [1+0j, 1+0j]])
    reference = iq([[1+0j, 1+0j], [1+0j, 1+0j]])
    for name, fn in receiver.DISPATCH.items():
        if name in receiver.CHANNEL_ESTIMATES:
            result = fn(received, reference)
            assert result["noise_variance"] == 0
        elif name in receiver.NOISE_ESTIMATES:
            result = fn(received)
            assert result["noise_variance"] == 0
        elif name in receiver.EQUALIZERS:
            result = fn(iq([2+0j, 1+0j]), iq([2+0j, 1+0j]))
            assert np.allclose(result["equalized_symbols"]["real"], [1, 1])
        else:
            result = fn(iq([1j, 1j]), iq([1+0j, 1+0j]))
            assert np.isclose(result["common_phase_error_rad"][0], np.pi/2)
        checked.add(name)

    for name, fn in bits.DISPATCH.items():
        result = fn(coded_bits=[0, 1, 1, 0] * 6)
        assert result["bit_count"] == 24
        checked.add(name)
    assert bits.recover("wlanLSIGRecover", coded_bits=[0]*24)["lsig"]["parity_ok"]

    for name, fn in fields.DISPATCH.items():
        args = ({} if name in fields.TRAINING else
                {"mcs": 0, "psdu_length": 1} if name == "wlanLSIG" else
                {"field_bits": [0]*24} if name in fields.SIGNAL else
                {"psdu_bits": [0, 1, 0, 1, 0, 1, 0, 1]})
        result = fn(**args)
        assert result["sample_count"] == len(result["waveform"]["real"])
        checked.add(name)
    assert fields.signal_field("wlanLSIG", 0, 100)["field_bits"][:4] == [1,1,0,1]
    sample_path = Path(__file__).resolve().parents[1] / "matlab_oracle" / "samples" / "wlan_extension.json"
    oracle = json.loads(sample_path.read_text(encoding="utf-8"))
    stf = fields._stf()
    oracle_stf = np.asarray(oracle["stf_real"]) + 1j*np.asarray(oracle["stf_imag"])
    assert np.max(abs(stf-oracle_stf)) < 1e-12
    lsig = fields.signal_field("wlanLSIG", 0, 1)
    oracle_lsig = np.asarray(oracle["lsig_real"]) + 1j*np.asarray(oracle["lsig_imag"])
    got_lsig = np.asarray(lsig["waveform"]["real"]) + 1j*np.asarray(lsig["waveform"]["imag"])
    assert lsig["field_bits"] == oracle["lsig_bits"]
    assert np.max(abs(got_lsig-oracle_lsig)) < 1e-12
    assert routing.wlan_bcc_interleave([i%2 for i in range(48)],48)["bits"] == oracle["interleave"]
    assert numeric.wlan_channel_frequency([1,6,14],2.4)["frequency_hz"] == oracle["channel_freq"]
    assert numeric.wlan_sample_rate("CBW20")["sample_rate_hz"] == oracle["sample_rate"]
    data_oracle = json.loads((sample_path.with_name("wlan_data_legacy.json")).read_text(encoding="utf-8"))
    data_python = fields.data_field("wlanNonHTData", [0,1,0,1,0,1,0,1])["waveform"]
    expected_data = np.asarray(data_oracle["real"]) + 1j*np.asarray(data_oracle["imag"])
    actual_data = np.asarray(data_python["real"]) + 1j*np.asarray(data_python["imag"])
    assert np.max(abs(actual_data - expected_data)) < 1e-12
    long_data = json.loads((sample_path.with_name("wlan_data_long.json")).read_text(encoding="utf-8"))
    for case in long_data:
        actual = fields.data_field("wlanNonHTData", case["bits"], mcs=case["mcs"])["waveform"]
        got = np.asarray(actual["real"]) + 1j * np.asarray(actual["imag"])
        want = np.asarray(case["real"]) + 1j * np.asarray(case["imag"])
        assert got.shape == want.shape and np.max(abs(got - want)) < 1e-12

    constellation_cases = json.loads((sample_path.with_name("wlan_constellation_full.json")).read_text(encoding="utf-8"))
    for case in constellation_cases:
        nbits = case["nbpscs"]
        patterns = np.arange(1 << nbits, dtype=np.uint16)
        binary = ((patterns[:, None] >> np.arange(nbits - 1, -1, -1)) & 1).astype(np.uint8).reshape(-1)
        mapped = constellation.constellation_map(binary, nbits)
        reference = np.asarray(case["real"]) + 1j * np.asarray(case["imag"])
        assert mapped.shape == reference.shape and np.max(abs(mapped - reference)) < 1e-12
        assert np.array_equal(constellation.constellation_demap(mapped, 0.01, nbits, "hard"), binary)

    frame = mac.mac_frame([1, 2, 3], source="001122334455")
    assert mac.mpdu_decode(frame["mpdu_hex"])["status"] == "Success"
    for name, fn in mac.DISPATCH.items():
        args = ({"ampdu": []} if name == "wlanAMPDUDeaggregate" else
                {"waveform": iq(fields._stf())} if name == "wlanFormatDetect" else
                {"payload": [1]} if name == "wlanMACFrame" else
                {"mpdu": frame["mpdu_hex"]} if name == "wlanMPDUDecode" else {})
        assert isinstance(fn(**args), dict)
        checked.add(name)

    for name, fn in channel.DISPATCH.items():
        args = ({"waveform": iq([1+0j, 0+0j]), "sample_rate_hz": 20e6, "seed": 1}
                if name in channel.CHANNELS else
                {"psdu_bits": [0,1,0,1,0,1,0,1]} if name == "wlanWaveformGenerator" else
                {"waveform": channel.waveform_generator([0,1,0,1,0,1,0,1])["waveform"]})
        result = fn(**args)
        assert isinstance(result, dict)
        checked.add(name)
    generated = channel.waveform_generator([0,1,0,1,0,1,0,1])
    analyzed = channel.waveform_analyzer(generated["waveform"])
    assert analyzed["format"] == "Non-HT" and generated["sample_count"] == 560
    expected = set().union(*(set(module.DISPATCH) for module in
                             (cfg, numeric, routing, ofdm, receiver, bits, fields, mac, channel)))
    assert checked == expected and len(checked) == 125
    root = Path(__file__).resolve().parents[1]
    registered = json.loads((root / "tool_registry.json").read_text(encoding="utf-8"))["tools"]
    wlan_records = [entry for entry in registered if entry["product"] == "WLAN Toolbox"]
    for module in (cfg, numeric, routing, ofdm, receiver, bits, fields, mac, channel):
        name = module.__name__
        record = next(entry for entry in wlan_records if entry["name"] == name)
        schema = json.loads((root / "tools" / f"{name}.schema.json").read_text(encoding="utf-8"))
        assert set(record["source_functions"]) == set(schema["inputs"]["function"]["enum"]) == set(module.DISPATCH)
    inventory = json.loads((root / "references" / "function_inventory.json").read_text(encoding="utf-8"))
    public = {entry["matlab_name"] for entry in inventory["products"]["WLAN Toolbox"]["functions"]}
    all_sources = [source for record in wlan_records for source in record["source_functions"]]
    assert len(public) == 137 and len(all_sources) == len(set(all_sources)) == 137
    assert set(all_sources) == public
    print(f"PASS {len(checked)} new WLAN source names and numerical invariants")


if __name__ == "__main__":
    main()
