"""Standalone single-port CSI-RS resource and CSI measurement subsets."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import complex_array, run_cli
from nr_csi_rs import csi_rs_rb_indices


def csirs_indices(nrb: int, symbol: int = 0, subcarrier_offset: int = 0,
                  density: int = 1, index_base: int = 1):
    """One NZP CSI-RS port, one OFDM symbol, density 0.5/1/3."""
    if not 1 <= nrb <= 275 or not 0 <= symbol < 14 or density not in (0, 1, 3):
        raise ValueError("invalid nrb, symbol or density")
    if not 0 <= subcarrier_offset < 12 or index_base not in (0, 1):
        raise ValueError("subcarrier_offset must be 0..11 and index_base 0/1")
    spacing = 4 if density == 3 else 12
    offsets = [(subcarrier_offset + i * spacing) % 12 for i in range(3 if density == 3 else 1)]
    indices = [index_base + symbol * nrb * 12 + int(rb) * 12 + sc
               for rb in csi_rs_rb_indices(nrb, density) for sc in offsets]
    return {"indices": indices, "n_re": len(indices), "index_base": index_base}


def csirs_measurements(grid, indices, nrb: int, index_base: int = 1):
    """RSRP/RSSI/RSRQ on an explicitly supplied single-port resource."""
    values = complex_array(grid)
    if values.ndim != 2 or values.shape[0] != 12 * nrb:
        raise ValueError("grid must have shape [12*nrb, symbols]")
    flat = values.reshape(-1, order="F")
    ix = np.asarray(indices, dtype=int).reshape(-1) - index_base
    if len(ix) == 0 or np.any(ix < 0) or np.any(ix >= flat.size):
        raise ValueError("indices must locate CSI-RS REs inside grid")
    rsrp = float(np.mean(abs(flat[ix]) ** 2))
    symbols = np.unique(ix // values.shape[0])
    rssi = float(np.mean(np.sum(abs(values[:, symbols]) ** 2, axis=0)))
    rsrq = float(nrb * rsrp / rssi) if rssi else 0.0
    return {"RSRP": rsrp, "RSSI": rssi, "RSRQ": rsrq,
            "RSRPdB": float(10 * np.log10(rsrp)) if rsrp else None,
            "RSRQdB": float(10 * np.log10(rsrq)) if rsrq else None}


def _wideband_quality(channel, noise_variance: float):
    h = complex_array(channel)
    if h.size == 0 or noise_variance <= 0 or not np.isfinite(noise_variance):
        raise ValueError("nonempty channel and positive noise_variance required")
    if h.ndim >= 2 and h.shape[-1] != 1:
        raise ValueError("this subset supports one transmit port")
    sinr = float(np.mean(abs(h) ** 2) / noise_variance)
    spectral_efficiency = float(np.log2(1 + sinr))
    return sinr, spectral_efficiency


def csi_report_csirs(channel, noise_variance: float):
    """Single-layer, single-port wideband estimate; CQI is an approximation."""
    sinr, efficiency = _wideband_quality(channel, noise_variance)
    # Conservative CQI-1 spectral efficiency thresholds from 38.214 Table 5.2.2.1-2.
    thresholds = [0, .1523, .2344, .3770, .6016, .8770, 1.1758, 1.4766,
                  1.9141, 2.4063, 2.7305, 3.3223, 3.9023, 4.5234,
                  5.1152, 5.5547]
    cqi = max(i for i, required in enumerate(thresholds) if required <= efficiency)
    return {"RI": 1, "PMI": 0, "CQI": cqi, "SINR": sinr,
            "spectral_efficiency_bound": efficiency}


def csi_measurements_srs(channel, noise_variance: float):
    """Single-TX-port wideband SRS quality estimate."""
    sinr, efficiency = _wideband_quality(channel, noise_variance)
    return {"Rank": 1, "TPMI": 0, "SINR": sinr,
            "SINRdB": float(10 * np.log10(sinr)) if sinr else None,
            "spectral_efficiency_bound": efficiency}


if __name__ == "__main__":
    run_cli("Standalone single-port CSI resource and quality subsets", {
        "nrCSIRSIndices": csirs_indices,
        "nrCSIRSMeasurements": csirs_measurements,
        "nrCSIReportCSIRS": csi_report_csirs,
        "nrCSIMeasurementsSRS": csi_measurements_srs,
    })
