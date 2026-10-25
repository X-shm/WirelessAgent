"""Cross-check the new 5G entry mappings with independent round trips."""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from nr_bch_codec import bch, bch_decode
from nr_channel_models import (tdl_channel, cdl_channel, hst_channel, path_loss,
                               perfect_channel_estimate, phase_noise)
from nr_control_codec import dci_decode, uci_encode, uci_decode
from nr_csi_resources import (csirs_indices, csirs_measurements,
                              csi_report_csirs, csi_measurements_srs)
from nr_dci import dci_encode
from nr_pdcch_resources import pdcch_resources, pdcch_space
from nr_prach_family import (prach, prach_detect, prach_grid, prach_indices,
                             prach_ofdm_info, prach_ofdm_modulate)
from nr_polar_rm import triangular_deinterleave, triangular_interleave
from nr_ptrs_family import (pdsch_ptrs, pdsch_ptrs_indices,
                            pusch_ptrs, pusch_ptrs_indices)
from nr_pucch_family import (pucch, pucch0, pucch1, pucch2, pucch3, pucch4,
                             pucch_decode, pucch_dmrs, pucch_dmrs_indices,
                             pucch_hopping_info, pucch_indices)
from nr_sch_transport import (dlsch_decoder, ulsch, ulsch_decoder,
                              ulsch_multiplex, ulsch_demultiplex)
from nr_waveform_io import waveform_generator, waveform_analyzer


def main() -> int:
    for length in (23, 108, 864):
        original = np.arange(length)
        assert np.array_equal(triangular_deinterleave(triangular_interleave(original)), original)
    payload = np.arange(12, dtype=np.uint8) % 2
    coded_dci = dci_encode(payload, 23, 108)
    decoded_dci = dci_decode((1 - 2 * coded_dci.astype(float)) * 20, 12, 23)
    assert decoded_dci["crc_ok"] and np.array_equal(decoded_dci["payload"], payload)
    assert not dci_decode((1 - 2 * coded_dci.astype(float)) * 20, 12, 24)["crc_ok"]
    coded_uci = uci_encode(payload, 108)["codeword"]
    # MATLAB R2026a U3: nrUCIEncode(mod((0:11)',2),108), first 64 bits.
    matlab_uci_prefix = [
        1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1,
        0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0,
        1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0,
        0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0,
    ]
    assert coded_uci[:64].tolist() == matlab_uci_prefix
    decoded_uci = uci_decode((1 - 2 * coded_uci.astype(float)) * 20, 12)
    assert decoded_uci["crc_ok"] and np.array_equal(decoded_uci["payload"], payload)

    mib = np.arange(24, dtype=np.uint8) % 2
    bch_bits = bch(mib, 42, 1, 4, 17, 321)["codeword"]
    # MATLAB R2026a U3: nrBCH(mod((0:23)',2),42,1,4,17,321), first 64 bits.
    matlab_bch_prefix = [
        1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1,
        1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1,
        0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0,
        1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1,
    ]
    assert bch_bits[:64].tolist() == matlab_bch_prefix
    decoded_bch = bch_decode((1 - 2 * bch_bits.astype(float)) * 30, 4, 321)
    assert decoded_bch["crc_ok"] and np.array_equal(decoded_bch["payload"], mib)
    assert decoded_bch["sfn_lsb"].tolist() == [1, 0, 1, 0]

    shifted = prach(1, 139, 17)["symbols"]
    detection = prach_detect(shifted, 1, 139)
    assert detection["detected"] and detection["cyclic_shift"] == 17
    assert len(prach_indices(139)["indices"]) == 139
    assert np.allclose(prach_grid(139, symbols=shifted)["grid"], shifted)
    assert prach_ofdm_info(139)["nfft"] == 256
    assert len(prach_ofdm_modulate(shifted, 256)["waveform"]) == 256
    impulse = tdl_channel([1, 0, 0], 1000, [0, .001], [1, .5])["samples"][:, 0]
    assert np.allclose(impulse, [1, .5, 0, 0])
    assert np.allclose(cdl_channel([1, 0], 1000, [0], [1])["samples"][:, 0], [1, 0])
    assert np.allclose(hst_channel([1, 0], 1000, 0, 3.5e9)["samples"][:, 0], [1, 0])
    assert np.allclose(phase_noise([1, 1], 1000, 0)["samples"], [1, 1])
    fspl = path_loss(3.5e9, [0, 0, 30], [100, 0, 1.5])["pathloss_db"]
    assert 80 < fspl < 90
    estimate = perfect_channel_estimate([1], [0], 1.92e6, 128, 12)["channel"]
    assert np.allclose(estimate, 1)

    indices = csirs_indices(2, 0, 0, 1)["indices"]
    grid = np.zeros((24, 14), complex)
    grid[np.asarray(indices) - 1, 0] = 1
    measured = csirs_measurements(grid, indices, 2)
    assert measured["RSRP"] == 1 and measured["RSRQ"] > 0
    assert csi_report_csirs([1], 1)["RI"] == 1
    assert csi_measurements_srs([1], 1)["Rank"] == 1
    resources = pdcch_resources(6)
    assert len(resources["indices"]) == 54 and len(resources["dmrs_indices"]) == 18
    assert len(pdcch_space(12, coreset_nrb=12,
                           num_candidates=[2, 1, 0, 0, 0])["candidates"]["1"]) == 2
    ptrs_i = pdsch_ptrs_indices(8, list(range(8)))
    ptrs_s = pdsch_ptrs(8, list(range(8)), 17)
    assert len(ptrs_i["indices"]) == len(ptrs_s["symbols"])
    assert len(pusch_ptrs_indices(8, list(range(8)))["indices"]) == len(
        pusch_ptrs(8, list(range(8)), 17)["symbols"])

    uci = [0, 1, 1, 0, 0, 1, 0, 1]
    short_symbols = pucch(0, ack=[1], nid=7)["symbols"]
    assert pucch_decode(short_symbols, 0, nid=7, ack_bits=1)["ack"] == [1]
    assert np.array_equal(short_symbols, pucch0([1], nid=7)["symbols"])
    long_symbols = pucch1([0, 1], nid=7)["symbols"]
    assert pucch_decode(long_symbols, 1, nid=7, num_symbols=4)["bits"].tolist() == [0, 1]
    for bit in (0, 1):
        one_bit_symbols = pucch1([bit], nid=7)["symbols"]
        decoded = pucch_decode(one_bit_symbols, 1, nid=7, num_symbols=4,
                               uci_bits_length=1)
        assert decoded["bits"].tolist() == [bit]
        assert len(decoded["llr"]) == 1
    assert len(pucch_indices(1, format_number=2, num_symbols=2)["indices"]) == 16
    assert len(pucch_dmrs_indices(1, format_number=2, num_symbols=2)["indices"]) == 8
    assert len(pucch_dmrs(7, format_number=2, num_symbols=2)["symbols"]) == 8
    assert len(pucch_hopping_info(7)["cyclic_shifts"]) == 14
    assert len(pucch2(uci, nid=7)["symbols"]) == 4
    assert len(pucch3(uci, nid=7)["symbols"]) == 4
    assert len(pucch4(uci, nid=7)["symbols"]) == 8
    for fmt in (2, 3, 4):
        symbols = pucch(fmt, uci_bits=uci, nid=7,
                        num_symbols=2 if fmt == 2 else 4)["symbols"]
        recovered = pucch_decode(symbols, fmt, nid=7)["bits"]
        assert recovered.tolist() == uci

    tb = np.arange(24, dtype=np.uint8) % 2
    codeword = ulsch(tb, .5, 672)["codeword"]
    recovered = ulsch_decoder((1 - 2 * codeword.astype(float)) * 20, 24, .5)
    assert recovered["crc_ok"] and np.array_equal(recovered["payload"], tb)
    assert dlsch_decoder((1 - 2 * codeword.astype(float)) * 20, 24, .5)["crc_ok"]
    combined = ulsch_multiplex([1, 0, 1], [0, 1], [1, 3], 5)["codeword"]
    split = ulsch_demultiplex(combined, [1, 3])
    assert split["data_bits"].tolist() == [1, 0, 1]
    assert split["uci_bits"].tolist() == [0, 1]

    resource_grid = np.zeros((12, 14), dtype=complex)
    resource_grid[3, 2] = 1 + 1j
    waveform = waveform_generator(resource_grid, 128)["waveform"]
    analysis = waveform_analyzer(waveform, 128, 1, 14)
    assert np.allclose(analysis["grid"], resource_grid, atol=1e-12)

    # Independent edge cases for each of the ten grouped tools.  These are
    # slice-level invariants, separate from the checked-in MATLAB oracle cases.
    for lssb, idxoffset in ((4, 17), (8, 17), (64, 37)):
        encoded = bch(mib, 1023, 0, lssb, idxoffset, 1007)["codeword"]
        decoded = bch_decode((1 - 2 * encoded.astype(float)) * 25, lssb, 1007)
        assert decoded["crc_ok"] and np.array_equal(decoded["payload"], mib)

    for length, e in ((19, 108), (20, 128), (100, 256)):
        data = np.arange(length, dtype=np.uint8) % 2
        encoded = uci_encode(data, e)["codeword"]
        decoded = uci_decode((1 - 2 * encoded.astype(float)) * 25, length)
        assert decoded["crc_ok"] and np.array_equal(decoded["payload"], data)

    mimo = tdl_channel([[1, 0], [0, 1]], 1000, [0],
                       [[[1, 0], [0, 1]]])["samples"]
    assert np.array_equal(mimo, np.eye(2))
    doppler = cdl_channel([1, 1], 1000, [0], [1], [250])["samples"][:, 0]
    assert np.allclose(doppler, [1, 1j], atol=1e-12)
    near = path_loss(3.5e9, [0, 0, 0], [100, 0, 0])["pathloss_db"]
    far = path_loss(3.5e9, [0, 0, 0], [200, 0, 0])["pathloss_db"]
    assert np.isclose(far - near, 20 * np.log10(2))
    noisy_phase = phase_noise([1] * 32, 1000, 10, seed=7)
    assert np.array_equal(noisy_phase["phase_radians"],
                          phase_noise([1] * 32, 1000, 10, seed=7)["phase_radians"])
    assert np.any(noisy_phase["phase_radians"] != 0)

    density_counts = [csirs_indices(4, density=d)["n_re"] for d in (0, 1, 3)]
    assert density_counts == [2, 4, 12]
    assert csirs_indices(2, symbol=3, subcarrier_offset=2)["indices"] == [75, 87]
    reference_grid = np.zeros((24, 1), dtype=complex)
    reference_grid[[2, 14], 0] = 2
    reference_csi = csirs_measurements(reference_grid, [3, 15], 2)
    assert reference_csi["RSRP"] == 4 and reference_csi["RSSI"] == 8
    assert reference_csi["RSRQ"] == 1
    first_based = csirs_indices(4, index_base=1)["indices"]
    zero_based = csirs_indices(4, index_base=0)["indices"]
    assert np.array_equal(np.asarray(first_based) - 1, zero_based)
    assert csi_report_csirs([1], .1)["CQI"] >= csi_report_csirs([1], 1)["CQI"]

    two_cce = pdcch_resources(12, coreset_nrb=12, aggregation_level=2)
    assert len(two_cce["indices"]) == 108 and len(two_cce["dmrs_indices"]) == 36
    assert not set(two_cce["indices"]) & set(two_cce["dmrs_indices"])
    assert max(two_cce["indices"] + two_cce["dmrs_indices"]) <= 12 * 12
    one_cce = pdcch_resources(6, symbol=1)
    assert one_cce["indices"][:9] == [73, 75, 76, 77, 79, 80, 81, 83, 84]
    assert one_cce["dmrs_indices"][:3] == [74, 78, 82]
    assert set(one_cce["indices"] + one_cce["dmrs_indices"]) == set(range(73, 145))

    long_prach = prach(7, 839, 37)["symbols"]
    long_detection = prach_detect(long_prach, 7, 839)
    assert long_detection["detected"] and long_detection["cyclic_shift"] == 37
    assert abs(np.vdot(long_prach, np.roll(long_prach, 1))) < 1e-8
    long_waveform = prach_ofdm_modulate(long_prach, 1024)["waveform"]
    assert len(long_waveform) == 1024
    assert np.isclose(np.sum(abs(long_waveform) ** 2), 839, atol=1e-8)
    unshifted_prach = prach(1, 139, 0)["symbols"]
    assert np.isclose(unshifted_prach[0], 1)
    assert np.isclose(unshifted_prach[1], np.exp(-2j * np.pi / 139))

    sparse_ptrs = pdsch_ptrs_indices(8, list(range(8)), dmrs_symbols=(2, 11),
                                    frequency_density=4, time_density=2)
    assert sparse_ptrs["n_re"] == len(sparse_ptrs["indices"])
    assert not {symbol for _, symbol in sparse_ptrs["subscripts"]} & {2, 11}
    assert len(pdsch_ptrs(8, list(range(8)), 17, dmrs_symbols=(2, 11),
                          frequency_density=4, time_density=2)["symbols"]) == sparse_ptrs["n_re"]
    reference_ptrs = pdsch_ptrs_indices(8, list(range(8)), num_symbols=4,
                                       dmrs_symbols=(1,), frequency_density=2,
                                       time_density=2, re_offset=3)
    assert reference_ptrs["indices"] == [4, 28, 52, 76, 292, 316, 340, 364]

    fmt1_indices = pucch_indices(1, num_symbols=4, format_number=1)
    assert {int((i - 1) // 12) for i in fmt1_indices["indices"]} == {1, 3}
    assert {int((i - 1) // 12) for i in fmt1_indices["dmrs_indices"]} == {0, 2}
    assert len(pucch_dmrs(7, format_number=1, num_symbols=4)["symbols"]) == 24

    for rv in range(4):
        encoded = ulsch(np.arange(100, dtype=np.uint8) % 2, .5, 1024, rv=rv)["codeword"]
        decoded = ulsch_decoder((1 - 2 * encoded.astype(float)) * 30,
                                100, .5, rv=rv, max_iter=20)
        assert decoded["crc_ok"] and np.array_equal(decoded["payload"],
                                                     np.arange(100) % 2)

    wider_grid = np.zeros((24, 14), dtype=complex)
    wider_grid[3, 2] = 1 + 1j
    wider_grid[15, 9] = -1 + 1j
    wider_waveform = waveform_generator(wider_grid, 256, scs_khz=30)
    wider_analysis = waveform_analyzer(wider_waveform["waveform"], 256, 2, 14,
                                       scs_khz=30)
    assert np.allclose(wider_analysis["grid"], wider_grid, atol=1e-12)

    root = Path(__file__).resolve().parents[1]
    for schema_path in sorted((root / "tools").glob("nr_*.schema.json")):
        if schema_path.stem.removesuffix(".schema") not in {
            "nr_bch_codec", "nr_channel_models", "nr_control_codec", "nr_csi_resources",
            "nr_pdcch_resources", "nr_prach_family", "nr_ptrs_family",
            "nr_pucch_family", "nr_sch_transport", "nr_waveform_io",
        }:
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        command = shlex.split(schema["example"]["cmd"])
        run = subprocess.run([sys.executable, *command[1:]], cwd=root,
                             capture_output=True, text=True, check=False)
        assert run.returncode == 0, (schema["name"], run.stdout, run.stderr)
        assert "error" not in json.loads(run.stdout), schema["name"]
    print("PASS NR remaining-entry independent integration checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
