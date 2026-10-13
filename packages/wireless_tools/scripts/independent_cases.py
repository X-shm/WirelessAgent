"""Independent standard/property tests for tools without saved MATLAB oracle data."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def test_awgn():
    from awgn import add_awgn
    x = np.ones(1000)
    y1, variance = add_awgn(x, 10, "measured", "db", 7)
    y2, _ = add_awgn(x, 10, "measured", "db", 7)
    assert variance == 0.1 and np.array_equal(y1, y2)


def test_biterr():
    from biterr import bit_errors
    num, ratio, individual, k = bit_errors([1, 2, 3], [1, 3, 0], 2)
    assert num == 3 and ratio == 0.5 and k == 2 and individual.tolist() == [0, 1, 2]


def test_symerr():
    from symerr import symbol_errors
    num, ratio, individual = symbol_errors([1, 2, 3], [1, 3, 0])
    assert num == 2 and abs(ratio - 2 / 3) < 1e-15 and individual.tolist() == [0, 1, 1]


def test_convert_snr():
    from convert_snr import convert_snr
    snr = convert_snr([6], "ebno", "snr", bits_per_symbol=2)[0]
    back = convert_snr([snr], "snr", "ebno", bits_per_symbol=2)[0]
    assert abs(snr - 9.010299956639813) < 1e-12 and abs(back - 6) < 1e-12


def test_zadoff_chu_seq():
    from zadoff_chu_seq import zadoff_chu_seq
    seq = zadoff_chu_seq(25, 63)
    corr = np.vdot(seq, np.roll(seq, 1))
    assert np.max(np.abs(np.abs(seq) - 1)) < 1e-14 and abs(corr) < 1e-10


def _slow_prbs(cinit, length, start=0):
    x1 = [1] + [0] * 30
    x2 = [(cinit >> bit) & 1 for bit in range(31)]
    for _ in range(1600 + start + length):
        x1.append(x1[3] ^ x1[0])
        x2.append(x2[3] ^ x2[2] ^ x2[1] ^ x2[0])
        x1.pop(0)
        x2.pop(0)
    # Registers now point after the requested sequence, so regenerate with direct indexing.
    n = 1600 + start + length + 31
    a = [0] * n
    b = [0] * n
    a[0] = 1
    for bit in range(31):
        b[bit] = (cinit >> bit) & 1
    for idx in range(n - 31):
        a[idx + 31] = a[idx + 3] ^ a[idx]
        b[idx + 31] = b[idx + 3] ^ b[idx + 2] ^ b[idx + 1] ^ b[idx]
    return np.array([a[1600 + start + i] ^ b[1600 + start + i] for i in range(length)])


def test_lte_prbs():
    from lte_prbs import lte_prbs
    expected = _slow_prbs(0x12345, 64, 17)
    got = lte_prbs(0x12345, 64, 17)
    signed = lte_prbs(0x12345, 64, 17, "signed")
    assert np.array_equal(got, expected) and np.array_equal(signed, 1 - 2 * got)


def test_lte_pss():
    from lte_pss import lte_pss
    seq = lte_pss(1, 0, "FDD")
    expected = np.array([1 + 0j, -0.969077286229078 - 0.246757397690294j,
                         -0.733051871829827 - 0.680172737770919j])
    assert len(seq) == 62 and np.max(np.abs(seq[:3] - expected)) < 1e-12
    assert len(lte_pss(1, 1, "FDD")) == 0


def test_node_position_grid():
    from node_position_grid import node_position_grid
    pos, cells = node_position_grid([100, 50], grid_size=[2, 2])
    assert pos == [[-25.0, 12.5, 0.0], [-25.0, -12.5, 0.0],
                   [25.0, 12.5, 0.0], [25.0, -12.5, 0.0]] and len(cells) == 4


def test_node_position_random():
    from node_position_random import node_position_random
    pos1, _ = node_position_random("circle", [10], num_nodes=100, seed=3)
    pos2, _ = node_position_random("circle", [10], num_nodes=100, seed=3)
    radius = np.linalg.norm(np.asarray(pos1)[:, :2], axis=1)
    assert pos1 == pos2 and np.max(radius) <= 10.01


def test_node_mobility_constant_velocity():
    from node_mobility_constant_velocity import constant_velocity
    got = constant_velocity([1, 2, 3], [10, -2, 0.5], [0, 1, 2])
    expected = np.array([[1, 2, 3], [11, 0, 3.5], [21, -2, 4]])
    assert np.array_equal(got, expected)


def test_qam_modulation():
    from qam_modulation import qam_modulate, qam_demodulate
    bits = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1])
    symbols, _ = qam_modulate(bits, 16)
    assert symbols[0] == -3 + 3j and np.array_equal(qam_demodulate(symbols, 16), bits)


def test_psk_modulation():
    from psk_modulation import psk_modulate, psk_demodulate
    bits = np.array([0, 0, 0, 1, 1, 0, 1, 1])
    symbols, _ = psk_modulate(bits, 4)
    assert np.max(np.abs(np.abs(symbols) - 1)) < 1e-15 and np.array_equal(psk_demodulate(symbols, 4), bits)


def test_pam_modulation():
    from pam_modulation import pam_modulate, pam_demodulate
    bits = np.array([0, 0, 0, 1, 1, 0, 1, 1])
    symbols, _ = pam_modulate(bits, 4)
    assert symbols.tolist() == [-3.0, -1.0, 3.0, 1.0] and np.array_equal(pam_demodulate(symbols, 4), bits)


def test_bit_int_conversion():
    from bit_int_conversion import bit_to_int, int_to_bit
    bits = np.array([1, 0, 1, 1, 0, 0])
    values = bit_to_int(bits, 2)
    assert values.tolist() == [2, 3, 0] and np.array_equal(int_to_bit(values, 2), bits)


def test_lte_sss():
    from lte_sss import lte_sss
    seq = lte_sss(1, 0)
    assert len(seq) == 62 and seq[:4].tolist() == [1, -1, 1, 1] and len(lte_sss(1, 1)) == 0


def test_lte_layer_map():
    from lte_layer_map import layer_map, layer_demap
    cw0 = np.arange(8) + 1j * np.arange(8)
    mapped = layer_map([cw0], 4)
    assert mapped.shape == (2, 4) and np.array_equal(layer_demap(mapped, 1)[0], cw0)
    cw1 = np.arange(100, 108) + 0j
    mapped2 = layer_map([cw0, cw1], 4)
    back = layer_demap(mapped2, 2)
    assert np.array_equal(back[0], cw0) and np.array_equal(back[1], cw1)


def test_node_mobility_random_walk():
    from node_mobility_random_walk import random_walk
    t1, p1, _ = random_walk([0, 0, 0], 5, 0.5, bounds=[0, 0, 10, 10], seed=4)
    t2, p2, _ = random_walk([0, 0, 0], 5, 0.5, bounds=[0, 0, 10, 10], seed=4)
    assert np.array_equal(t1, t2) and np.array_equal(p1, p2) and np.max(np.abs(p1[:, :2])) <= 5.000001


def test_node_mobility_random_waypoint():
    from node_mobility_random_waypoint import random_waypoint
    _, p1, _ = random_waypoint([0, 0, 0], 5, 0.5, bounds=[0, 0, 10, 10], seed=5)
    _, p2, _ = random_waypoint([0, 0, 0], 5, 0.5, bounds=[0, 0, 10, 10], seed=5)
    assert np.array_equal(p1, p2) and np.max(np.abs(p1[:, :2])) <= 5.000001


def test_wireless_packet():
    from wireless_packet import wireless_packet
    packet = wireless_packet(TransmitterID=1, Duration=0.001, Power=20)
    assert packet["TechnologyType"] == 0 and packet["TransmitterVelocity"] == [0, 0, 0]
    assert packet["TransmitterID"] == 1 and packet["Metadata"]["Channel"]["PathGains"] == []


def test_dpsk_modulation():
    from dpsk_modulation import dpsk_modulate, dpsk_demodulate
    labels = np.array([0, 1, 3, 2, 2, 0, 1])
    for order in ("binary", "gray"):
        symbols = dpsk_modulate(labels, 4, 0.2, order)
        assert np.array_equal(dpsk_demodulate(symbols, 4, 0.2, order), labels)


def test_fsk_modulation():
    from fsk_modulation import fsk_modulate, fsk_demodulate
    labels = np.array([0, 1, 3, 2, 0])
    waveform = fsk_modulate(labels, 4, 100, 32, 2000, "continuous", "gray")
    assert np.array_equal(fsk_demodulate(waveform, 4, 100, 32, 2000, "gray"), labels)


def test_ofdm_modulation():
    from ofdm_modulation import ofdm_modulate, ofdm_demodulate
    rng = np.random.default_rng(8)
    nulls, pilots_idx = [1, 5], [3]
    data = rng.normal(size=(5, 3)) + 1j * rng.normal(size=(5, 3))
    pilots = np.ones((1, 3), complex)
    waveform = ofdm_modulate(data, 8, [2, 3, 2], nulls, pilots_idx, pilots)
    got, got_pilots = ofdm_demodulate(waveform, 8, [2, 3, 2], None, nulls, pilots_idx)
    assert np.max(np.abs(got - data)) < 1e-12 and np.max(np.abs(got_pilots - pilots)) < 1e-12


def test_binary_symmetric_channel():
    from binary_symmetric_channel import bsc
    data = np.array([0, 1, 1, 0])
    assert np.array_equal(bsc(data, 0, 1)[0], data)
    assert np.array_equal(bsc(data, 1, 1)[0], 1 - data)


def test_white_gaussian_noise():
    from white_gaussian_noise import wgn
    x = wgn(200000, 1, 0, 1, "dbw", "complex", 9)
    y = wgn(200000, 1, 0, 1, "dbw", "complex", 9)
    assert np.array_equal(x, y) and abs(float(np.mean(np.abs(x) ** 2)) - 1) < 0.015


def test_frequency_offset():
    from frequency_offset import apply_frequency_offset
    x = np.ones(128, complex)
    y = apply_frequency_offset(x, 1024, 32)
    back = apply_frequency_offset(y, 1024, -32)
    assert np.max(np.abs(back[:, 0] - x)) < 1e-14


def test_rectangular_pulse():
    from rectangular_pulse import rectangular_pulse
    assert rectangular_pulse([1, 2], 3).tolist() == [1, 1, 1, 2, 2, 2]


def test_lte_convolutional_codec():
    from lte_convolutional_codec import convolutional_encode, convolutional_decode
    bits = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1])
    coded = convolutional_encode(bits)
    decoded, metric = convolutional_decode(coded)
    assert len(coded) == 3 * len(bits) and metric == 0 and np.array_equal(decoded, bits)


def test_lte_resource_grid():
    from lte_resource_grid import resource_grid_size
    assert resource_grid_size("downlink", 6, "Normal", 2) == [72, 14, 2]
    assert resource_grid_size("uplink", 100, "Extended", 4) == [1200, 12, 4]


def test_lte_code_block():
    from lte_code_block import segment, desegment
    rng = np.random.default_rng(10)
    for length, sizes in ((100, [104]), (6144, [6144]), (6145, [3072, 3136]), (12000, None)):
        bits = rng.integers(0, 2, length)
        blocks, params = segment(bits)
        recovered, errors, _ = desegment(blocks, length)
        assert np.array_equal(recovered, bits) and not any(errors)
        if sizes is not None:
            assert [len(block) for block in blocks] == sizes


def test_lte_rate_match_convolutional():
    from lte_rate_match_convolutional import rate_match, rate_recover
    x = np.arange(132, dtype=float)
    matched = rate_match(x, 132)
    recovered = rate_recover(matched, 132)
    repeated = rate_recover(rate_match(x, 264), 132)
    assert np.array_equal(recovered, x) and np.array_equal(repeated, 2 * x)


def test_convolutional_codec():
    from convolutional_codec import encode, decode_hard
    bits = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0])
    coded, state = encode(bits, 3, [0o7, 0o5])
    decoded, metric = decode_hard(coded, 3, [0o7, 0o5])
    assert len(coded) == 2 * len(bits) and metric == 0 and np.array_equal(decoded, bits)


def test_interleaver():
    from interleaver import permutation, interleave
    data = np.arange(12)
    for kind, kwargs in (("matrix", {"rows": 3, "columns": 4}), ("random", {"seed": 11}),
                         ("explicit", {"indices": list(reversed(range(12)))})):
        perm = permutation(len(data), kind, **kwargs)
        assert np.array_equal(interleave(interleave(data, perm), perm, "deinterleave"), data)


def test_hamming_code():
    from hamming_code import encode_block, decode_block
    message = np.array([1, 0, 1, 1])
    code = encode_block(message, 3)
    for position in range(7):
        damaged = code.copy(); damaged[position] ^= 1
        got, corrected, syndrome = decode_block(damaged, 3)
        assert np.array_equal(got, message) and np.array_equal(corrected, code) and syndrome == position + 1


def test_reed_solomon_code():
    from _gf import GF2m
    from reed_solomon_code import encode, decode
    rng = np.random.default_rng(20)
    for m, n, k in ((3, 7, 3), (4, 15, 9), (8, 31, 23)):
        gf = GF2m(m)
        t = (n - k) // 2
        for parity in ("end", "beginning"):
            message = rng.integers(0, 1 << m, k).tolist()
            codeword, _ = encode(message, n, k, gf, parity)
            damaged = codeword.copy()
            for position in rng.choice(n, t, replace=False):
                damaged[int(position)] ^= int(rng.integers(1, 1 << m))
            decoded, corrected, errors = decode(damaged, n, k, gf, parity)
            assert decoded == message and corrected == codeword and errors == t


def test_bch_code():
    from bch_code import encode, decode
    rng = np.random.default_rng(21)
    for n, k in ((7, 4), (15, 7), (31, 16)):
        message = rng.integers(0, 2, k)
        codeword, _, t = encode(message, n, k)
        damaged = codeword.copy()
        damaged[rng.choice(n, t, replace=False)] ^= 1
        decoded, corrected, errors, _ = decode(damaged, n, k)
        assert np.array_equal(decoded, message) and np.array_equal(corrected, codeword) and errors == t


def test_q_function():
    from q_function import qfunc, qfuncinv
    assert qfunc(0) == 0.5
    for value in (-3.0, -1.0, 0.0, 1.0, 3.0):
        assert abs(qfuncinv(qfunc(value)) - value) < 1e-10


def test_ber_awgn():
    from ber_awgn import ber_awgn
    ber, ser = ber_awgn([0.0, 10.0], "bpsk")
    assert abs(ber[0] - 0.07864960352514257) < 1e-15 and ber == ser
    qber, qser = ber_awgn([0.0], "qam", 16)
    assert 0 < qber[0] < qser[0] < 1
    fcoh, _ = ber_awgn([5.0], "fsk", 2, False, "coherent")
    fnon, _ = ber_awgn([5.0], "fsk", 2, False, "noncoherent")
    assert fcoh[0] < fnon[0]


def test_fading_channel():
    from fading_channel import flat_fading
    signal = np.ones(200000, complex)
    output1, gains1 = flat_fading(signal, "rayleigh", seed=22)
    output2, gains2 = flat_fading(signal, "rayleigh", seed=22)
    assert np.array_equal(output1, output2) and np.array_equal(gains1, gains2)
    assert abs(float(np.mean(np.abs(gains1) ** 2)) - 1.0) < 0.015
    _, block = flat_fading(np.ones(12), "rician", 5.0, 23, 3)
    assert np.all(block.reshape(-1, 3) == block.reshape(-1, 3)[:, :1])


def test_evm_metrics():
    from evm_metrics import evm
    reference = np.ones(100, complex)
    normalized, rms, peak, rms_db = evm(reference + 0.1, reference)
    assert np.max(np.abs(normalized - 0.1)) < 1e-14
    assert abs(rms - 0.1) < 1e-14 and abs(peak - 0.1) < 1e-14 and abs(rms_db + 20) < 1e-12


def test_lte_frequency_sync():
    from lte_frequency_sync import estimate_frequency_offset, correct_frequency_offset
    rng = np.random.default_rng(30)
    nfft, cp, sample_rate, expected = 64, 16, 960000.0, 123.4
    symbols = []
    for _ in range(5):
        body = rng.normal(size=nfft) + 1j*rng.normal(size=nfft)
        symbols.extend([*body[-cp:], *body])
    original = np.asarray(symbols)
    shifted = original * np.exp(1j*2*np.pi*expected*np.arange(len(original))/sample_rate)
    estimated, _, _ = estimate_frequency_offset(shifted, sample_rate, nfft, cp)
    corrected = correct_frequency_offset(shifted, sample_rate, estimated)
    assert abs(estimated - expected) < 1e-8 and np.max(np.abs(corrected - original)) < 1e-10


def test_ofdm_equalizer():
    from ofdm_equalizer import equalize
    rng = np.random.default_rng(31)
    channel = rng.normal(size=(20, 2, 2)) + 1j*rng.normal(size=(20, 2, 2))
    symbols = rng.normal(size=(20, 2)) + 1j*rng.normal(size=(20, 2))
    received = np.einsum("nij,nj->ni", channel, symbols)
    for algorithm in ("zf", "mmse"):
        output, csi = equalize(received, channel, 0, algorithm)
        assert np.max(np.abs(output-symbols)) < 1e-10 and np.all(csi >= 0)


def test_signal_timing_estimate():
    from signal_timing_estimate import timing_estimate, channel_delay
    rng = np.random.default_rng(32)
    reference = rng.normal(size=64) + 1j*rng.normal(size=64)
    waveform = np.r_[np.zeros(7), reference, np.zeros(4)]
    offset, correlation = timing_estimate(waveform, reference)
    assert offset == 7 and np.max(correlation) > 0.999999
    delay, magnitude, _ = channel_delay(np.array([[1, 0.6]]), np.array([[0, 1, 0], [0, 0, 2]]))
    assert delay == 2 and magnitude.shape == (3, 1)


def test_ofdm_channel_estimate():
    from ofdm_channel_estimate import channel_estimate
    expected = 2 + 1j
    grid = np.ones((8, 4), complex) * expected
    indices = [[carrier, symbol] for symbol in (0, 3) for carrier in (0, 2, 5, 7)]
    estimate, pilots, noise = channel_estimate(grid, np.ones(8), indices)
    assert np.max(np.abs(estimate-expected)) < 1e-14 and np.max(np.abs(pilots-expected)) < 1e-14 and noise < 1e-20


def test_lte_cell_rs():
    from lte_cell_rs import cell_rs
    result = cell_rs(6, 10, 0, "Normal", [0, 1, 2, 3])
    assert [len(result[port]["symbols"]) for port in range(4)] == [48, 48, 24, 24]
    assert result[2]["indices"][:4].tolist() == [[4, 1, 2], [10, 1, 2], [16, 1, 2], [22, 1, 2]]
    assert np.max(np.abs(np.abs(result[0]["symbols"])-1)) < 1e-14


def test_lte_sync_indices():
    from lte_sync_indices import sync_indices
    result = sync_indices(6, 0, "Normal")
    assert len(result["pss"]) == 62 and len(result["sss"]) == 62
    assert result["pss"][0] == [5, 6, 0] and result["sss"][0] == [5, 5, 0]
    assert sync_indices(50, 1)["pss"] == []


def test_lte_cell_search():
    from lte_cell_search import cell_search
    from lte_pss import lte_pss
    from lte_sss import lte_sss
    for ncellid, subframe in ((0, 0), (321, 0), (503, 5)):
        result = cell_search(lte_pss(ncellid, 0), lte_sss(ncellid, subframe), subframe)
        assert result["ncellid"] == ncellid and result["pss_score"] > 0.999999 and result["sss_score"] > 0.999999


def test_lte_extract_resources():
    from lte_extract_resources import extract_resources
    grid = np.arange(24).reshape((4, 3, 2), order="F")
    values, subs = extract_resources(grid, [[0, 0, 0], [3, 2, 1]])
    linear, linear_subs = extract_resources(grid, [0, 23], "linear")
    assert values.tolist() == [0, 23] and linear.tolist() == [0, 23]
    assert np.array_equal(subs, linear_subs)


def test_lte_dl_channel_estimate():
    from lte_cell_rs import cell_rs
    from lte_dl_channel_estimate import dl_channel_estimate
    nrb, ncellid, ports = 6, 42, [0, 1]
    references = cell_rs(nrb, ncellid, 0, "Normal", ports)
    expected = [2+1j, -0.5+0.25j]
    grid = np.zeros((72, 14), complex)
    for port, channel in zip(ports, expected):
        indices = references[port]["indices"]
        grid[indices[:, 0], indices[:, 1]] += channel*references[port]["symbols"]
    estimate, noise = dl_channel_estimate(grid, nrb, ncellid, 0, "Normal", ports)
    for port_index, channel in enumerate(expected):
        assert np.max(np.abs(estimate[:, :, 0, port_index]-channel)) < 1e-12
    assert noise < 1e-20


def test_lte_pusch_dmrs():
    from lte_pusch_dmrs import pusch_dmrs
    dmrs = pusch_dmrs(15, 42, [0, 1, 2], 0, "Normal", 0, 0, 3)
    assert len(dmrs) == 2
    assert dmrs[0]["indices"][0].tolist() == [0, 3, 0]
    assert dmrs[1]["indices"][0].tolist() == [0, 10, 0]
    for slot in dmrs:
        assert slot["symbols"].size == 36
        assert np.max(np.abs(np.abs(slot["symbols"]) - 1.0)) < 1e-12


def test_lte_ul_channel_estimate():
    from lte_pusch_dmrs import pusch_dmrs
    from lte_ul_channel_estimate import ul_channel_estimate
    nrb, ncellid, prb = 15, 42, [0, 1, 2]
    dmrs = pusch_dmrs(nrb, ncellid, prb, 0, "Normal", 0, 0, 3)
    channel = 1.5 - 0.25j
    grid = np.zeros((12*nrb, 14), complex)
    for slot in dmrs:
        indices = slot["indices"]
        grid[indices[:, 0], indices[:, 1]] = channel*slot["symbols"]
    estimate, noise = ul_channel_estimate(grid, nrb, ncellid, prb, 0, "Normal", 0, 0, 3)
    assert np.max(np.abs(estimate[:36, :, 0] - channel)) < 1e-12
    assert noise < 1e-20


def test_lte_ul_scrambling():
    from lte_ul_scrambling import scramble, descramble_soft
    rng = np.random.default_rng(2048)
    bits = rng.integers(0, 2, 257, dtype=np.uint8)
    scrambled, _ = scramble(bits, 7, 42, 321, 0)
    llr = 1.0 - 2.0*scrambled.astype(float)
    recovered_llr, _ = descramble_soft(llr, 7, 42, 321, 0)
    assert np.array_equal(recovered_llr, 1.0 - 2.0*bits.astype(float))


def test_lte_scfdma():
    from lte_scfdma import scfdma_info, scfdma_modulate, scfdma_demodulate
    rng = np.random.default_rng(2049)
    grid = rng.normal(size=(72, 14)) + 1j*rng.normal(size=(72, 14))
    waveform, _ = scfdma_modulate(grid, 6, "Normal")
    recovered, _ = scfdma_demodulate(waveform, 6, "Normal")
    assert scfdma_info(6, "Normal")["nfft"] == 128
    assert np.max(np.abs(recovered[:, :, 0]-grid)) < 1e-11


def test_lte_frame_offset():
    from lte_frame_offset import frame_offset
    rng = np.random.default_rng(2050)
    reference = rng.normal(size=80) + 1j*rng.normal(size=80)
    received = np.concatenate((np.zeros(9, complex), reference, np.zeros(20, complex)))
    offset, _ = frame_offset(received, reference, 200, 0)
    assert offset == 9


def test_lte_pusch_indices():
    from lte_pusch_indices import pusch_indices
    ports, info = pusch_indices(6, [0], "Normal", False, 1, "QPSK", 1)
    indices = ports["0"]
    assert info["Gd"] == 144 and info["G"] == [288]
    assert indices[0].tolist() == [0, 0, 0]
    assert not np.any(np.isin(indices[:, 1], [3, 10]))
    _, shortened = pusch_indices(6, [0], "Normal", True, 1, "QPSK", 1)
    assert shortened["Gd"] == 132


def test_lte_pdsch_indices():
    from lte_pdsch_indices import pdsch_indices
    indices, info = pdsch_indices(6, 0, [1, 2, 3, 4, 5], 1, 1, "Normal", 4, "TxDiversity", "QPSK", 1)
    linear = indices[:, 0] + 72*indices[:, 1]
    assert linear[:7].tolist() == [156, 157, 158, 159, 160, 161, 162]
    assert info["Gd"] == len(indices) and info["G"] == [2*len(indices)]
    sync_indices, _ = pdsch_indices(6, 0, list(range(6)), 5, 1, "Normal", 1)
    central = set(range(5, 67))
    assert not any(symbol in (5, 6) and carrier in central for carrier, symbol, _ in sync_indices)


def test_lte_srs():
    from lte_srs import srs
    sequence, indices, info = srs(15, [0, 1, 2, 3, 4, 5], 0, "Normal", 1, 3, 4, 0)
    assert len(sequence) == 36 and indices[0].tolist() == [1, 13, 0]
    assert np.all(np.diff(indices[:, 0]) == 2)
    assert np.max(np.abs(np.abs(sequence)-1.0)) < 1e-12
    assert info["Alpha"] == 3*np.pi/4 and info["KTxComb"] == 1


def test_lte_pmi_info():
    from lte_pmi_info import pmi_info
    assert pmi_info(50, 4, 1, "Wideband", 1, "SpatialMux") == {
        "k": 50, "NSubbands": 1, "MaxPMI": 15, "CodebookSubsetSize": 16}
    assert pmi_info(50, 2, 1, "Subband", 2, "SpatialMux") == {
        "k": 6, "NSubbands": 9, "MaxPMI": 1, "CodebookSubsetSize": 6}


def test_lte_csi_codebook():
    from lte_csi_codebook import csi_codebook, dl_precode, dl_deprecode
    expected = np.asarray([[1], [1j]])/np.sqrt(2)
    assert np.max(np.abs(csi_codebook(1, 2, 2)-expected)) < 1e-12
    rng = np.random.default_rng(2051)
    layers = rng.normal(size=(30, 2)) + 1j*rng.normal(size=(30, 2))
    antennas, _ = dl_precode(layers, 2, 1)
    recovered, _ = dl_deprecode(antennas, 2, 1)
    assert np.max(np.abs(recovered-layers)) < 1e-12


def test_lte_pmi_select():
    from lte_pmi_select import pmi_select
    channel = np.zeros((72, 14, 1, 2), complex)
    channel[:, :, :, 0] = 1
    channel[:, :, :, 1] = 1
    selected, _ = pmi_select(channel, 0.1, 6, 1, "Wideband")
    assert selected == [0]
    channel[:, :, :, 1] = -1
    selected, _ = pmi_select(channel, 0.1, 6, 1, "Wideband")
    assert selected == [1]


def test_lte_ul_precode():
    from lte_ul_precode import ul_precode
    rng = np.random.default_rng(2052)
    symbols = rng.normal(size=(144, 2)) + 1j*rng.normal(size=(144, 2))
    precoded = ul_precode(symbols, 6, "PRB")
    recovered = ul_precode(precoded, 6, "PRB", True)
    assert np.max(np.abs(recovered-symbols)) < 1e-12
    assert np.max(np.abs(np.sum(np.abs(precoded)**2, axis=0)-np.sum(np.abs(symbols)**2, axis=0))) < 1e-10


def test_lte_mimo_equalizer():
    from lte_mimo_equalizer import mimo_equalize
    from lte_csi_codebook import csi_codebook
    rng = np.random.default_rng(2053)
    layers = rng.normal(size=(50, 2)) + 1j*rng.normal(size=(50, 2))
    precoder = csi_codebook(2, 2, 0)
    channel = np.tile(np.eye(2), (50, 1, 1))
    received = layers@precoder.T
    recovered, csi, _ = mimo_equalize(received, channel, 0, 2, 0)
    assert np.max(np.abs(recovered-layers)) < 1e-11 and np.all(csi > 0)


def test_lte_pdsch_prbs():
    from lte_pdsch_prbs import pdsch_prbs
    from lte_ul_scrambling import scrambling_sequence
    sequence, cinit = pdsch_prbs(42, 7, 321, 0, 100)
    expected, expected_cinit = scrambling_sequence(100, 7, 42, 321, 0)
    assert cinit == expected_cinit and np.array_equal(sequence, expected)
    signed, _ = pdsch_prbs(42, 7, 321, 0, 20, 10, "signed")
    assert set(signed.tolist()) <= {-1, 1}


def test_lte_standard_fading():
    from lte_standard_fading import channel_profile, apply_fading
    assert [len(channel_profile(name)["delays_ns"]) for name in ("EPA", "EVA", "ETU")] == [7, 9, 9]
    signal = np.zeros(100, complex)
    signal[0] = 1
    first, gains, _ = apply_fading(signal, 30.72e6, "EPA", 0, 4)
    second, _, _ = apply_fading(signal, 30.72e6, "EPA", 0, 4)
    assert first.shape == (100, 1) and gains.shape == (100, 7)
    assert np.array_equal(first, second)


def test_ofdm_channel_response():
    from ofdm_channel_response import channel_response
    gains = np.full((80, 1), 2+1j)
    response = channel_response(gains, [[1]], 64, 16)
    assert response.shape == (64, 1, 1, 1)
    assert np.max(np.abs(response-(2+1j))) < 1e-12


def test_ber_fading():
    from ber_fading import ber_fading
    for ebno_db in (-5, 0, 10):
        gamma = 10**(ebno_db/10)
        expected = 0.5*(1-np.sqrt(gamma/(1+gamma)))
        assert abs(ber_fading(ebno_db)-expected) < 2e-8
    assert ber_fading(10, diversity_order=2) < ber_fading(10, diversity_order=1)


def test_link_capacity():
    from link_capacity import link_capacity
    assert abs(link_capacity(0, 1e6)["capacity_bps"]-1e6) < 1e-9
    identity = link_capacity(0, 1e6, np.eye(2))
    assert identity["spectral_efficiency_bps_hz"] > 1


def test_radio_link_diagnosis():
    from radio_link_diagnosis import diagnose
    result = diagnose(snr_db=0, frequency_offset_hz=3000)
    assert result["status"] == "critical" and result["finding_count"] >= 2
    assert diagnose(snr_db=20, evm_percent=2, ber=0)["status"] == "ok"


def test_link_adaptation_optimizer():
    from link_adaptation_optimizer import optimize_link
    low = optimize_link(0, 25)
    high = optimize_link(20, 25)
    assert high["recommended_mcs"] > low["recommended_mcs"]
    assert high["tbs_bits_per_subframe"] > low["tbs_bits_per_subframe"]


def test_resource_allocation_optimizer():
    from resource_allocation_optimizer import allocate_resources
    users = [{"id": "a", "snr_db": 15, "demand_kbps": 5000}, {"id": "b", "snr_db": 5, "demand_kbps": 2000}]
    result = allocate_resources(users, 10)
    assert result["allocated_prbs"] == 10
    assert sum(item["allocated_prbs"] for item in result["allocations"]) == 10


def test_closed_loop_validator():
    from closed_loop_validator import validate_closed_loop
    result = validate_closed_loop({"throughput": 10, "ber": 0.01}, {"throughput": 12, "ber": 0.001}, {"ber": {"max": 0.002}})
    assert result["accepted"] and not result["rollback_recommended"]
    failed = validate_closed_loop({"throughput": 10}, {"throughput": 9}, {"throughput": {"min": 10}})
    assert not failed["accepted"] and failed["rollback_recommended"]


def test_ber_coding():
    from ber_coding import ber_coding
    assert ber_coding(10, "hamming", "hard", n=7) < ber_coding(0, "hamming", "hard", n=7)
    soft = ber_coding([0, 5, 10], "conv", "soft", code_rate=0.5, d_free=5, weights=[1, 2, 4])
    assert soft[0] > soft[1] > soft[2]


def test_lte_rank_select():
    from lte_rank_select import rank_select
    orthogonal = np.zeros((72, 14, 2, 2), complex)
    orthogonal[:] = np.eye(2)
    assert rank_select(orthogonal, 0.01, 6)["ri"] == 2
    correlated = np.zeros((72, 14, 1, 2), complex)
    correlated[:, :, :, 0] = 1
    correlated[:, :, :, 1] = 1
    assert rank_select(correlated, 0.1, 6)["ri"] == 1


def test_lte_cqi_select():
    from lte_cqi_select import cqi_select
    assert cqi_select([-20], "Port0")["wideband_cqi"] == 0
    assert cqi_select([30], "Port0")["wideband_cqi"] == 15
    report = cqi_select([0, 10, 20], "SpatialMux", "Subband")
    assert len(report["cqi_report"]) == 4
    assert all(-1 <= value <= 2 for value in report["subband_offset_levels"])


def test_traffic_steering_optimizer():
    from traffic_steering_optimizer import steer_traffic
    flows = [{"id": "f1", "required_kbps": 1000, "max_latency_ms": 20, "priority": 2}, {"id": "f2", "required_kbps": 500, "max_latency_ms": 100}]
    accesses = [{"id": "lte", "capacity_kbps": 2000, "latency_ms": 15, "snr_db": 15}, {"id": "wifi", "capacity_kbps": 2000, "latency_ms": 40, "snr_db": 25}]
    result = steer_traffic(flows, accesses)
    assert len(result["assignments"]) == 2 and result["unserved_flow_count"] == 0
    assert result["assignments"][0]["access_id"] == "lte"


def test_qos_policy_builder():
    from qos_policy_builder import build_qos_policy
    policy = build_qos_policy([{"id": "v", "service_type": "voice", "guaranteed_kbps": 100, "max_kbps": 200}], 1000)
    assert policy["capacity_feasible"] and policy["qos_data"][0]["five_qi"] == 1
    assert policy["qos_data"][0]["resource_type"] == "GBR"


def test_policy_decision_validator():
    from qos_policy_builder import build_qos_policy
    from policy_decision_validator import validate_policy
    qos = build_qos_policy([{"id": "v", "service_type": "voice", "guaranteed_kbps": 100, "max_kbps": 200}], 1000)["qos_data"]
    assert validate_policy(qos, 1000, {"v": {"latency_ms": 50, "packet_error_rate": 0.001}})["accepted"]
    assert not validate_policy(qos, 50)["accepted"]


def test_nr_modulation():
    from nr_modulation import demodulate, modulate

    rng = np.random.default_rng(38211)
    bits_per_symbol = {
        "BPSK": 1,
        "pi/2-BPSK": 1,
        "QPSK": 2,
        "16QAM": 4,
        "64QAM": 6,
        "256QAM": 8,
        "1024QAM": 10,
    }
    for modulation, width in bits_per_symbol.items():
        bits = rng.integers(0, 2, 12 * width, dtype=int)
        symbols = modulate(bits, modulation)
        assert np.array_equal(demodulate(symbols, modulation), bits)

    known = modulate(np.array([0, 1, 0, 1]), "pi/2-BPSK")
    expected = np.array([1 + 1j, 1 - 1j, 1 + 1j, 1 - 1j]) / np.sqrt(2.0)
    assert np.allclose(known, expected, atol=1e-15)


CASES = {
    "awgn": test_awgn,
    "biterr": test_biterr,
    "symerr": test_symerr,
    "convert_snr": test_convert_snr,
    "zadoff_chu_seq": test_zadoff_chu_seq,
    "lte_prbs": test_lte_prbs,
    "lte_pss": test_lte_pss,
    "node_position_grid": test_node_position_grid,
    "node_position_random": test_node_position_random,
    "node_mobility_constant_velocity": test_node_mobility_constant_velocity,
    "qam_modulation": test_qam_modulation,
    "psk_modulation": test_psk_modulation,
    "pam_modulation": test_pam_modulation,
    "bit_int_conversion": test_bit_int_conversion,
    "lte_sss": test_lte_sss,
    "lte_layer_map": test_lte_layer_map,
    "node_mobility_random_walk": test_node_mobility_random_walk,
    "node_mobility_random_waypoint": test_node_mobility_random_waypoint,
    "wireless_packet": test_wireless_packet,
    "dpsk_modulation": test_dpsk_modulation,
    "fsk_modulation": test_fsk_modulation,
    "ofdm_modulation": test_ofdm_modulation,
    "binary_symmetric_channel": test_binary_symmetric_channel,
    "white_gaussian_noise": test_white_gaussian_noise,
    "frequency_offset": test_frequency_offset,
    "rectangular_pulse": test_rectangular_pulse,
    "lte_convolutional_codec": test_lte_convolutional_codec,
    "lte_resource_grid": test_lte_resource_grid,
    "lte_code_block": test_lte_code_block,
    "lte_rate_match_convolutional": test_lte_rate_match_convolutional,
    "convolutional_codec": test_convolutional_codec,
    "interleaver": test_interleaver,
    "hamming_code": test_hamming_code,
    "reed_solomon_code": test_reed_solomon_code,
    "bch_code": test_bch_code,
    "q_function": test_q_function,
    "ber_awgn": test_ber_awgn,
    "fading_channel": test_fading_channel,
    "evm_metrics": test_evm_metrics,
    "lte_frequency_sync": test_lte_frequency_sync,
    "ofdm_equalizer": test_ofdm_equalizer,
    "signal_timing_estimate": test_signal_timing_estimate,
    "ofdm_channel_estimate": test_ofdm_channel_estimate,
    "lte_cell_rs": test_lte_cell_rs,
    "lte_sync_indices": test_lte_sync_indices,
    "lte_cell_search": test_lte_cell_search,
    "lte_extract_resources": test_lte_extract_resources,
    "lte_dl_channel_estimate": test_lte_dl_channel_estimate,
    "lte_pusch_dmrs": test_lte_pusch_dmrs,
    "lte_ul_channel_estimate": test_lte_ul_channel_estimate,
    "lte_ul_scrambling": test_lte_ul_scrambling,
    "lte_scfdma": test_lte_scfdma,
    "lte_frame_offset": test_lte_frame_offset,
    "lte_pusch_indices": test_lte_pusch_indices,
    "lte_pdsch_indices": test_lte_pdsch_indices,
    "lte_srs": test_lte_srs,
    "lte_pmi_info": test_lte_pmi_info,
    "lte_csi_codebook": test_lte_csi_codebook,
    "lte_pmi_select": test_lte_pmi_select,
    "lte_ul_precode": test_lte_ul_precode,
    "lte_mimo_equalizer": test_lte_mimo_equalizer,
    "lte_pdsch_prbs": test_lte_pdsch_prbs,
    "lte_standard_fading": test_lte_standard_fading,
    "ofdm_channel_response": test_ofdm_channel_response,
    "ber_fading": test_ber_fading,
    "link_capacity": test_link_capacity,
    "radio_link_diagnosis": test_radio_link_diagnosis,
    "link_adaptation_optimizer": test_link_adaptation_optimizer,
    "resource_allocation_optimizer": test_resource_allocation_optimizer,
    "closed_loop_validator": test_closed_loop_validator,
    "ber_coding": test_ber_coding,
    "lte_rank_select": test_lte_rank_select,
    "lte_cqi_select": test_lte_cqi_select,
    "traffic_steering_optimizer": test_traffic_steering_optimizer,
    "qos_policy_builder": test_qos_policy_builder,
    "policy_decision_validator": test_policy_decision_validator,
    "nr_modulation": test_nr_modulation,
}


def run(name):
    try:
        CASES[name]()
        print(f"PASS {name} independent standard/property tests")
        print("\n1/1 passed")
        return 0
    except Exception as exc:
        print(f"FAIL {name}: {exc}")
        print("\n0/1 passed")
        return 1
