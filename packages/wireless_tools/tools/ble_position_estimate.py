"""Estimate a Bluetooth LE node position from angles and/or ranges."""
from __future__ import annotations

import math
import numpy as np

from _bluetooth_common import InputError, run_cli


def _matrix(value, name):
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} must be a numeric matrix") from exc
    if array.ndim != 2 or not np.isfinite(array).all():
        raise InputError(f"{name} must be a finite numeric matrix")
    return array


def _vector(value, name):
    try:
        array = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} must be a numeric vector") from exc
    if not np.isfinite(array).all():
        raise InputError(f"{name} must be finite")
    return array


def estimate(locator_positions, method: str, *, distance=None, direction=None) -> np.ndarray:
    locators = _matrix(locator_positions, "locator_positions")
    dimensions, count = locators.shape
    if dimensions not in (2, 3):
        raise InputError("locator_positions must have two or three coordinate rows")
    if method not in {"angulation", "lateration", "distance-angle"}:
        raise InputError("method must be angulation, lateration, or distance-angle")
    if method == "lateration":
        ranges = _vector(distance, "distance")
        if count <= dimensions or ranges.size != count or np.any(ranges < 0):
            raise InputError("lateration requires more locators than dimensions and one nonnegative distance per locator")
        a = 2 * (locators[:, :-1] - locators[:, [-1]]).T
        b = (np.sum(locators[:, :-1] ** 2 - locators[:, [-1]] ** 2, axis=0)
             + ranges[-1] ** 2 - ranges[:-1] ** 2)
        return np.linalg.solve(a.T @ a, a.T @ b)
    try:
        directions = np.asarray(direction, dtype=float)
    except (TypeError, ValueError) as exc:
        raise InputError("direction must be a numeric vector or matrix") from exc
    if dimensions == 2 and directions.ndim == 1:
        directions = directions[np.newaxis, :]
    if directions.ndim != 2 or not np.isfinite(directions).all():
        raise InputError("direction must be a finite numeric vector or matrix")
    if directions.shape != (dimensions - 1, count):
        raise InputError("direction must have one azimuth row (2-D) or azimuth/elevation rows (3-D) per locator")
    azimuth = directions[0]
    if np.any(np.abs(azimuth) > 180) or (dimensions == 3 and np.any(np.abs(directions[1]) > 90)):
        raise InputError("azimuth must be in -180..180 and elevation in -90..90")
    if method == "distance-angle":
        ranges = _vector(distance, "distance")
        if ranges.size != count or np.any(ranges < 0):
            raise InputError("distance-angle requires one nonnegative distance per locator")
        if dimensions == 2:
            incident = np.vstack((np.cos(np.deg2rad(azimuth)), np.sin(np.deg2rad(azimuth))))
        else:
            elevation = directions[1]
            incident = np.vstack((np.cos(np.deg2rad(elevation)) * np.cos(np.deg2rad(azimuth)),
                                  np.cos(np.deg2rad(elevation)) * np.sin(np.deg2rad(azimuth)),
                                  np.sin(np.deg2rad(elevation))))
        return np.mean(locators + ranges * incident, axis=1)
    if count < dimensions - 1:
        raise InputError("angulation requires at least dimensions-1 locators")
    x, y = locators[0].copy(), locators[1].copy()
    tangent = np.tan(np.deg2rad(azimuth))
    if dimensions == 3:
        elevation = directions[1]
        # This is the same branch selection used by blePositionEstimate.
        const_zy = np.tan(np.deg2rad(elevation)) / np.sin(np.deg2rad(azimuth))
        use_xy = (np.all(np.round(const_zy) == np.round(const_zy[0]))
                  or np.any(np.abs(azimuth) < 10))
    else:
        use_xy = True
    if use_xy:
        a = np.column_stack((tangent, -np.ones(count)))
        b = x * tangent - y
        positive = np.isposinf(tangent)
        negative = np.isneginf(tangent)
        a[positive] = (1, 0); b[positive] = x[positive]
        a[negative] = (-1, 0); b[negative] = -x[negative]
        xy = np.linalg.solve(a.T @ a, a.T @ b)
        if dimensions == 2:
            return xy
        horizontal = np.sqrt((xy[0] - x) ** 2 + (xy[1] - y) ** 2)
        return np.array([xy[0], xy[1], np.mean(locators[2] + horizontal * np.tan(np.deg2rad(elevation)))])
    # For nearly equal 3-D azimuths MathWorks resolves the position in the
    # z/y plane first, then derives x from the remaining angular bearings.
    z = locators[2]
    a_zy = np.column_stack((np.ones(count), -const_zy))
    b_zy = z - y * const_zy
    remove = np.zeros(count, dtype=bool)
    positive = np.isposinf(const_zy)
    negative = np.isneginf(const_zy)
    a_zy[positive] = (-1, 0); b_zy[positive] = -y[positive]
    a_zy[negative] = (1, 0); b_zy[negative] = y[negative]
    remove |= positive | negative
    zy = np.linalg.solve(a_zy.T @ a_zy, a_zy.T @ b_zy)
    remaining_x = x[~remove]
    remaining_y = y[~remove]
    remaining_tangent = tangent[~remove]
    pos_x = (zy[1] - remaining_y) / remaining_tangent + remaining_x
    max_index = int(np.argmax(np.abs(pos_x)))
    if np.any(np.abs(pos_x[max_index]) - np.abs(pos_x) > 20):
        pos_x = np.delete(pos_x, max_index)
    return np.array([np.mean(pos_x), zy[1], zy[0]])


def _handler(_args, request):
    position = estimate(request.get("locator_positions"), request.get("method"),
                        distance=request.get("distance"), direction=request.get("direction"))
    return {"result": {"position": position.tolist()}}


if __name__ == "__main__":
    run_cli("ble_position_estimate", _handler, description=__doc__)
