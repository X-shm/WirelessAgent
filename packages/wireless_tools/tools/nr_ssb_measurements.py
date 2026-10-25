"""Standalone SSB RSRP, RSSI and RSRQ measurements without phase correction."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from _complex_io import parse_complex
from nr_pbch_ref import pbch_dmrs, pbch_dmrs_indices
from nr_sss import sss


def _decibels(power: float, milliwatts: bool = True) -> float | None:
    if power <= 0:
        return None
    return float(10 * np.log10(power * (1000 if milliwatts else 1)))


def ssb_measurements(ssb_grid: np.ndarray, ncellid: int,
                     ibar_ssb: int | None = None) -> dict:
    grid = np.asarray(ssb_grid, dtype=complex)
    if grid.ndim == 0:
        grid = np.full((240, 4), grid.item(), dtype=complex)
    if grid.ndim == 2:
        grid = grid[:, :, np.newaxis]
    if grid.ndim != 3 or grid.shape[:2] != (240, 4) or grid.shape[2] < 1:
        raise ValueError("ssb_grid must be 240 x 4 x NRx; a scalar fills one grid")
    if type(ncellid) is not int or not 0 <= ncellid <= 1007:
        raise ValueError("ncellid must be 0..1007")
    if ibar_ssb is not None and (type(ibar_ssb) is not int or not 0 <= ibar_ssb <= 7):
        raise ValueError("ibar_ssb must be 0..7")
    if not np.all(np.isfinite(grid)):
        raise ValueError("ssb_grid must contain finite values")
    reference_sss = sss(ncellid)
    sss_power = np.abs(np.mean(grid[56:183, 2, :] * reference_sss[:, np.newaxis], axis=0)) ** 2
    if ibar_ssb is None:
        rsrp_power = sss_power
    else:
        positions = pbch_dmrs_indices(ncellid)
        dmrs_grid = grid.reshape((960, grid.shape[2]), order="F")[positions]
        reference_dmrs = pbch_dmrs(ncellid, ibar_ssb)
        dmrs_power = np.abs(np.mean(dmrs_grid * np.conj(reference_dmrs[:, np.newaxis]), axis=0)) ** 2
        rsrp_power = (127 * sss_power + 144 * dmrs_power) / 271
    rssi_power = np.sum(np.abs(grid) ** 2, axis=(0, 1)) / 4
    return {
        "RSRPPerAntenna": [_decibels(float(power)) for power in rsrp_power],
        "RSSIPerAntenna": [_decibels(float(power)) for power in rssi_power],
        "RSRQPerAntenna": [
            _decibels(float(20 * rsrp / rssi), milliwatts=False) if rssi > 0 else None
            for rsrp, rssi in zip(rsrp_power, rssi_power)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent SSB RSRP/RSSI/RSRQ")
    parser.add_argument("--ssb_grid", required=True, help="Complex JSON 240 x 4 x NRx grid; scalar fills grid")
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--ibar_ssb", type=int, help="Include PBCH DM-RS in RSRP")
    args = parser.parse_args()
    try:
        print(json.dumps(ssb_measurements(parse_complex(args.ssb_grid),
                                           args.ncellid, args.ibar_ssb), allow_nan=False))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
