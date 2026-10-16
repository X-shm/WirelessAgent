"""Check newly ported NR primitives against development-time MATLAB outputs."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from nr_channel_prbs import channel_prbs
from nr_channel_estimate import channel_estimate_sparse
from nr_config import available_configs, make_config
from nr_evm import measure_evm
from nr_grid_ops import extract_resources, resource_grid
from nr_pdcch import pdcch
from nr_pdcch_decode import pdcch_decode
from nr_pdsch_decode import pdsch_decode
from nr_pdsch_grid_indices import pdsch_grid_indices
from nr_pdsch_precode import pdsch_precode
from nr_perfect_timing import perfect_timing
from nr_modulation import modulate
from nr_oran_bfp import bfp_compress, bfp_decompress
from nr_ofdm_info import ofdm_info
from nr_layer_map import layer_map
from nr_low_papr import low_papr_type1
from nr_prbs import prbs
from nr_polar import polar_encode
from nr_polar_decode import polar_decode_sc
from nr_pusch_scrambling import descramble, scramble
from nr_pusch_codebook import pusch_codebook, _codebook
from nr_prg_info import prg_info
from nr_prs import prs_resource
from nr_sch_info import sch_info
from nr_ssb_measurements import ssb_measurements
from nr_tables import lookup
from nr_transform import transform


def main() -> int:
    configs = available_configs()
    assert len(configs) == 38
    assert all(make_config(name)["properties"] == defaults for name, defaults in configs.items())
    carrier = make_config("nrCarrierConfig", {"NSizeGrid": 10, "SubcarrierSpacing": 30})["properties"]
    assert (carrier["NSizeGrid"], carrier["SlotsPerSubframe"], carrier["SlotsPerFrame"]) == (10, 2, 20)
    assert make_config("nrPDSCHConfig", {"DMRS": {"DMRSAdditionalPosition": 1}})["properties"]["DMRS"]["DMRSAdditionalPosition"] == 1
    # MATLAB R2026a U3: nrPBCHPRBS(42,2,16)
    expected_pbch = [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1]
    assert channel_prbs("pbch", 42, 16, v=2) == (42, expected_pbch)
    # MATLAB: nrPDSCHPRBS(42,100,0,16), nrPUSCHPRBS(42,100,16),
    # and nrPUCCHPRBS(42,100,16) all return the same base Gold sequence.
    expected_shared = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0]
    for channel in ("pdsch", "pusch", "pucch"):
        assert channel_prbs(channel, 42, 16, rnti=100) == (3276842, expected_shared)
    assert channel_prbs("pdsch", 42, 8, rnti=100, q=1) == (3293226, [1, 0, 0, 1, 0, 0, 0, 0])
    assert channel_prbs("pusch", 42, 8, rnti=100, q=1) == (3293226, [1, 0, 0, 1, 0, 0, 0, 0])
    assert scramble(np.array([0, 1, 0, 1, 1, 0, 0, 1]), 42, 100).tolist() == [1, 1, 1, 0, 1, 0, 1, 1]
    assert descramble(np.array([2, -3, 4, -5, 6, -7, 8, -9]), 42, 100).tolist() == [-2, -3, -4, 5, 6, -7, -8, -9]
    rx_grid = np.zeros((12, 14), dtype=complex)
    ref_grid = np.zeros((12, 14), dtype=complex)
    ref_grid[0, 2], ref_grid[6, 9] = 1 + 1j, 2
    rx_grid[0, 2], rx_grid[6, 9] = 2 + 3j, 6
    h, nvar, info = channel_estimate_sparse(rx_grid, ref_grid)
    # MATLAB: nrChannelEstimate(rxGrid,refGrid,'Interpolation','off')
    assert h.shape == (12, 14, 1) and np.count_nonzero(h) == 2
    assert h[0, 2, 0] == 2.5 + 0.5j and h[6, 9, 0] == 3
    assert nvar == 0 and info == {"AveragingWindow": [1, 1]}
    # MATLAB: nrSSBMeasurements(ones(240,4),42) with/without ibarSSB=0.
    ssb = ssb_measurements(np.ones((240, 4)), 42)
    assert abs(ssb["RSRPPerAntenna"][0] - (-12.076074419119138)) < 1e-11
    assert abs(ssb["RSSIPerAntenna"][0] - 53.802112417116064) < 1e-11
    assert abs(ssb["RSRQPerAntenna"][0] - (-52.867886879595389)) < 1e-11
    ssb_dmrs = ssb_measurements(np.ones((240, 4)), 42, 0)
    assert abs(ssb_dmrs["RSRPPerAntenna"][0] - 5.2638305639666711) < 1e-11
    assert len(_codebook()) == 4542
    # MATLAB: nrPUSCHCodebook(2,4,7) = [0.5 0 0.5 0; 0 0.5 0 0.5i].
    assert np.array_equal(pusch_codebook(2, 4, 7),
                          np.array([[0.5, 0, 0.5, 0], [0, 0.5, 0, 0.5j]]))
    assert pusch_codebook(1, 1, 0).tolist() == [[1 + 0j]]
    assert prg_info(10, 3, 4) == {"NPRG": 4, "PRGSet": [1, 2, 2, 2, 2, 3, 3, 3, 3, 4]}
    assert prg_info(10, 3) == {"NPRG": 1, "PRGSet": [1] * 10}
    cqi = lookup("cqi", "CQITable1", 1)["row"]
    assert cqi == {"CQIIndex": 1, "Modulation": "QPSK", "Qm": 2,
                   "TargetCodeRate": 0.076171875, "SpectralEfficiency": 0.1523}
    assert lookup("pusch", "QAM64Table", 0)["row"]["MCSIndex"] == 0
    assert sch_info(8456, 517 / 1024) == {"CRC": "24A", "L": 24, "BGN": 1, "C": 2,
                                        "Lcb": 24, "F": 312, "Zc": 208, "K": 4576, "N": 13728}
    assert sch_info(24, 0.5)["F"] == 30
    assert sch_info(3825, 0.2)["C"] == 2
    assert sch_info(0, 0.5) == {"CRC": "16", "L": 0, "BGN": 2, "C": 1,
                                   "Lcb": 0, "F": 0, "Zc": 2, "K": 0, "N": 0}
    assert sch_info(8456, 517 / 1024, uplink=True)["GULSCH"] == []
    dci_bits = np.array([0, 1, 1, 0, 0, 0, 1, 1])
    assert np.allclose(pdcch_decode(pdcch(dci_bits, 42, 100), 42, 100, 1),
                       [2, -2, -2, 2, 2, 2, -2, -2])
    pdsch_symbols = layer_map(modulate(dci_bits ^ prbs((100 << 15) + 42, len(dci_bits)), "QPSK"), 2)
    pdsch_llr, constellation = pdsch_decode(pdsch_symbols, "QPSK", 42, 100, 1)
    assert np.allclose(pdsch_llr, [2, -2, -2, 2, 2, 2, -2, -2])
    assert np.allclose(constellation[0], -1 / np.sqrt(2) - 1j / np.sqrt(2))
    dmrs_indices = pdsch_grid_indices("dmrs", 1, [0], [0, 14], [2, 11])
    assert dmrs_indices["indices"] == [25, 27, 29, 31, 33, 35, 133, 135, 137, 139, 141, 143]
    data_indices = pdsch_grid_indices("data", 1, [0], [0, 14], [2, 11])
    assert data_indices["n_indices"] == 144 and data_indices["info"] == {
        "G": 288, "Gd": 144, "DMRSSymbolSet": [2, 11]}
    sparse = pdsch_grid_indices("dmrs", 3, [0, 2], [0, 4], [2], 2, 2)
    assert sparse["indices"] == [73, 74, 79, 80, 97, 98, 103, 104]
    assert pdsch_grid_indices("data", 3, [0, 2], [0, 4], [2], 2, 2)["info"]["Gd"] == 80
    # MATLAB: nrPDSCHPrecode(nrCarrierConfig(NSizeGrid=2),portSym,portInd,W)
    ant_sym, ant_ind = pdsch_precode(
        np.array([[1 + 1j, 2], [3, 4 + 2j], [5, 6]]),
        np.array([[1, 1], [13, 13], [25, 25]]),
        np.array([[[1], [2]], [[3], [4]]]), 2,
    )
    assert np.array_equal(ant_sym, [[7 + 1j, 10 + 2j], [15 + 6j, 22 + 8j], [23, 34]])
    assert ant_ind.tolist() == [[1, 337], [13, 349], [25, 361]]
    block = np.arange(1, 13) + 1j * np.arange(-12, 0)
    compressed, exponents = bfp_compress(block, 4)
    assert exponents.tolist() == [1]
    assert compressed.real.tolist() == [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6]
    assert compressed.imag.tolist() == [-6, -5, -5, -4, -4, -3, -3, -2, -2, -1, -1, 0]
    assert np.allclose(bfp_decompress(compressed, exponents), 2 * compressed)
    ofdm15 = ofdm_info(1, 15, windowing=0)
    assert (ofdm15["Nfft"], ofdm15["SampleRate"], ofdm15["CyclicPrefixLengths"]) == (
        128, 1920000, [10] + [9] * 6 + [10] + [9] * 6)
    ofdm30 = ofdm_info(52, 30, windowing=0)
    assert ofdm30["Nfft"] == 1024 and ofdm30["CyclicPrefixLengths"][:14] == [88] + [72] * 13
    assert ofdm_info(150, 60, cyclic_prefix="extended", windowing=0)["CyclicPrefixLengths"] == [1024] * 48

    # MATLAB R2026a U3: nrLowPAPRS(9,0,2*pi,36) and nrLowPAPRS(7,1,pi/2,72)
    assert np.allclose(low_papr_type1(9, 0, 2 * np.pi, 36).ravel()[:4], [
        1 + 0j, -0.44039415155763462 - 0.89780453957074147j,
        0.97952994125249437 + 0.20129852008866067j,
        0.91895781162023 + 0.39435585511331994j,
    ])
    assert np.allclose(low_papr_type1(7, 1, np.pi / 2, 72).ravel()[:4], [
        1 + 0j, 0.99388790402955074 - 0.11039399541526965j,
        -0.32580057296011738 - 0.94543851553597036j,
        0.61604882012036388 + 0.78770797331771847j,
    ])
    assert np.allclose(low_papr_type1(0, 0, 0, 6).ravel(),
                       np.exp(1j * np.array([-3, -1, 3, 3, -1, -3]) * np.pi / 4))
    assert low_papr_type1([0, 9], 0, [0, np.pi], 36).shape == (36, 2, 2, 1)
    # MATLAB: nrPolarDecode(20*(1-2*double(nrPolarEncode(x,64))),40,64,1)
    polar_message = np.array([(i * 7 + 3) % 2 for i in range(40)], dtype=np.int8)
    polar_coded = polar_encode(polar_message, 64)
    assert polar_coded[:12].tolist() == [0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1]
    assert np.array_equal(polar_decode_sc(20 * (1 - 2 * polar_coded.astype(float)), 40, 64),
                          polar_message)
    # MATLAB: nrPRS/nrPRSIndices, one active PRS resource in carrier grid.
    prs_indices, prs_symbols = prs_resource(4, 2, 1, 0, 2, 2, 0, 0)
    assert prs_indices[:12] == list(range(13, 37, 2)) and prs_indices[12:16] == [62, 64, 66, 68]
    assert np.allclose(prs_symbols[:6], np.array([
        -1 + 1j, -1 - 1j, -1 - 1j, 1 - 1j, 1 + 1j, -1 - 1j,
    ]) / np.sqrt(2))
    prs_indices, prs_symbols = prs_resource(4, 4, 0, 3, 4, 4, 1, 7, slot=1)
    assert prs_indices[:12] == list(range(146, 194, 4))
    assert np.allclose(prs_symbols[:4], np.array([-1 + 1j, -1 - 1j, -1 - 1j, 1 + 1j]) / np.sqrt(2))
    _, prs_slot2 = prs_resource(2, 2, 0, 0, 2, 2, 0, 0, slot=2)
    assert np.allclose(prs_slot2[:4], np.array([-1 - 1j, 1 + 1j, -1 - 1j, 1 - 1j]) / np.sqrt(2))
    path_gains = np.zeros((2, 2, 2, 1), dtype=complex)
    path_gains[:, 0, 0, 0] = [1, -1]
    path_gains[:, 0, 1, 0] = [-3, 3]
    path_gains[:, 1, 0, 0] = [2, 2]
    path_gains[:, 1, 1, 0] = [-4, -4]
    offset, magnitude = perfect_timing(path_gains, np.array([[1, 0], [0, 1], [0, 0]]))
    # MATLAB: nrPerfectTimingEstimate(pathGains,pathFilters)
    assert offset == 1 and magnitude[:, 0].tolist() == [0, 2, 0]

    x = np.arange(1, 25) + 1j * np.arange(24, 0, -1)
    transformed = transform(x, 1)
    # MATLAB: nrTransformPrecode((1:24).'+1i*(24:-1:1).',1)
    expected_first = np.array([
        22.5166604983954 + 64.0858798800485j,
        4.73205080756888 + 8.19615242270663j,
        1.26794919243112 + 4.73205080756888j,
        0 + 3.46410161513775j,
    ])
    assert np.allclose(transformed[:4], expected_first, atol=1e-12)
    assert np.allclose(transform(transformed, 1, inverse=True), x, atol=1e-12)
    matrix = np.column_stack((x, 2 * x))
    assert np.allclose(transform(matrix, 1)[:, 1], 2 * transformed)

    assert resource_grid(1, 2).shape == (12, 14, 2)
    assert resource_grid(1, 1, "extended").shape == (12, 12, 1)
    sample_grid = np.arange(1, 13).reshape((3, 2, 2), order="F")
    resources, indices = extract_resources(np.array([1, 3]), sample_grid)
    # MATLAB: [re,ri]=nrExtractResources([1;3],reshape(1:12,3,2,2))
    assert resources.tolist() == [[1, 7], [3, 9]]
    assert indices.tolist() == [[1, 7], [3, 9]]
    wrapped, wrapped_indices = extract_resources(np.array([7]), sample_grid)
    assert wrapped.tolist() == [[1, 7]] and wrapped_indices.tolist() == [[1, 7]]
    subscripts, sub_indices = extract_resources(np.array([[1, 1, 1], [3, 1, 1]]), sample_grid, index_style="subscript")
    assert np.array_equal(subscripts, resources)
    assert sub_indices.tolist() == [[1, 1, 1], [3, 1, 1], [1, 1, 2], [3, 1, 2]]

    equalized = np.array([[1 + 1j, 0], [2 - 1j, 1j]])
    reference = np.array([[1, 0], [2, 1j]])
    rms, peak, error = measure_evm(equalized, reference)
    # MATLAB: nrEVM(equalized,reference)
    assert abs(rms - 0.57735026918953) < 1e-12
    assert abs(peak - 0.70710678118643) < 1e-12
    assert np.allclose(error, np.array([[1j / np.sqrt(2), 0], [-1j / np.sqrt(2), 0]]))
    print("PASS 22 independent NR tools / 69 source entry points against MATLAB R2026a development samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
