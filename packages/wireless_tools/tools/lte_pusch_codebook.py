"""Standalone LTE uplink PUSCH MIMO codebook and PMI geometry."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_RECORDS = json.loads(Path(__file__).with_name("_lte_pusch_codebook.json")
                      .read_text(encoding="utf-8"))
_BOOK = {}
for _record in _RECORDS:
    _key = (_record["antennas"], _record["layers"], _record["pmi"])
    _matrix = (np.asarray(_record["matrix_real"], dtype=float) +
               1j*np.asarray(_record["matrix_imag"], dtype=float))
    _BOOK[_key] = _matrix.reshape(_record["layers"], _record["antennas"])
_MAX_PMI = {(1, 1): 0, (2, 1): 5, (2, 2): 0,
            (4, 1): 23, (4, 2): 15, (4, 3): 11, (4, 4): 0}


def ul_pmi_info(nrb=6, n_tx_ants=1, n_layers=1):
    nrb, antennas, layers = int(nrb), int(n_tx_ants), int(n_layers)
    if not 1 <= nrb <= 110 or (antennas, layers) not in _MAX_PMI:
        raise ValueError("invalid uplink bandwidth, antennas, or layers")
    return {"k": nrb, "NSubbands": 1,
            "MaxPMI": _MAX_PMI[(antennas, layers)]}


def pusch_codebook(values, n_tx_ants=1, n_layers=None, pmi=0, inverse=False):
    data = np.asarray(values, dtype=complex)
    if data.ndim == 1:
        data = data[:, None]
    if data.ndim != 2 or data.shape[0] == 0:
        raise ValueError("symbols must be a nonempty matrix")
    antennas = int(n_tx_ants)
    layers = int(data.shape[1] if n_layers is None and not inverse else
                 1 if n_layers is None else n_layers)
    key = (antennas, layers, int(pmi))
    if key not in _BOOK:
        raise ValueError("invalid antenna/layer/PMI combination")
    expected_columns = antennas if inverse else layers
    if data.shape[1] != expected_columns:
        raise ValueError("symbol matrix columns do not match antenna/layer count")
    matrix = _BOOK[key]
    return data @ (np.linalg.pinv(matrix) if inverse else matrix)
