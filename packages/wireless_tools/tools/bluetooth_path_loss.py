"""Calculate Bluetooth BR/EDR or LE propagation path loss."""
from __future__ import annotations

import numpy as np

from _bluetooth_common import InputError, run_cli


WAVELENGTH = 0.1229  # c / 2.44 GHz, the bluetoothPathLossConfig constant


def _values(value, name, size, *, lower=None, upper=None, positive=False):
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} must be a number or numeric array") from exc
    if array.ndim > 1 or array.size == 0 or not np.isfinite(array).all():
        raise InputError(f"{name} must be a finite scalar or one-dimensional array")
    if array.size == 1:
        array = np.full(size, float(array.item()))
    elif array.size != size:
        raise InputError(f"{name} must be scalar or contain one value per distance")
    if (lower is not None and np.any(array < lower)) or (upper is not None and np.any(array > upper)):
        raise InputError(f"{name} is outside its allowed range")
    if positive and np.any(array <= 0):
        raise InputError(f"{name} must be positive")
    return array


def path_loss(distance, *, environment="Outdoor", transmitter_antenna_gain=0,
              receiver_antenna_gain=0, transmitter_cable_loss=0,
              receiver_cable_loss=0, transmitter_antenna_height=1,
              receiver_antenna_height=1, path_loss_exponent=2.2,
              standard_deviation=2.667, random_stream="Global stream", seed=73,
              shadow_fading_db=None):
    distance = _values(distance, "distance", np.asarray(distance).size, lower=0)
    size = distance.size
    if environment not in {"Outdoor", "Industrial", "Home", "Office"}:
        raise InputError("environment must be Outdoor, Industrial, Home, or Office")
    tx_gain = _values(transmitter_antenna_gain, "transmitter_antenna_gain", size, lower=-10, upper=10)
    rx_gain = _values(receiver_antenna_gain, "receiver_antenna_gain", size, lower=-10, upper=10)
    tx_loss = _values(transmitter_cable_loss, "transmitter_cable_loss", size, lower=0)
    rx_loss = _values(receiver_cable_loss, "receiver_cable_loss", size, lower=0)
    if environment == "Industrial":
        exponent = _values(path_loss_exponent, "path_loss_exponent", size, positive=True)
        stddev = _values(standard_deviation, "standard_deviation", size, lower=0)
        with np.errstate(divide="ignore"):
            deterministic = 20 * np.log10(4 * np.pi / WAVELENGTH) + 10 * exponent * np.log10(distance)
    elif environment == "Outdoor":
        tx_height = _values(transmitter_antenna_height, "transmitter_antenna_height", size, positive=True)
        rx_height = _values(receiver_antenna_height, "receiver_antenna_height", size, positive=True)
        stddev = _values(standard_deviation, "standard_deviation", size, lower=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            phi = np.arctan((tx_height + rx_height) / distance)
            los = np.sqrt((tx_height - rx_height) ** 2 + distance ** 2)
            reflected = np.sqrt((tx_height + rx_height) ** 2 + distance ** 2)
            gamma = (18 * np.sin(phi) - np.sqrt(18 - np.cos(phi) ** 2)) / (18 * np.sin(phi) + np.sqrt(18 - np.cos(phi) ** 2))
            inverse = (WAVELENGTH / (4 * np.pi * los)) ** 2 + (WAVELENGTH / (4 * np.pi * reflected)) ** 2 * gamma * np.cos((reflected - los) * 2 * np.pi / WAVELENGTH)
            deterministic = 10 * np.log10(1 / inverse)
    else:
        if environment == "Home":
            p0, first_exp, second_exp, breakpoint, stddev = 12.5, 4.2, 7.6, 11.0, np.full(size, 3.0)
        else:
            p0, first_exp, second_exp, breakpoint, stddev = 26.8, 4.2, 8.7, 10.0, np.full(size, 3.7)
        with np.errstate(divide="ignore"):
            deterministic = np.where(
                distance <= breakpoint,
                p0 + 10 * first_exp * np.log10(distance),
                p0 + 10 * first_exp * np.log10(breakpoint) + 10 * second_exp * np.log10(distance / breakpoint),
            )
    if shadow_fading_db is not None:
        fading = _values(shadow_fading_db, "shadow_fading_db", size)
    elif np.all(stddev == 0):
        fading = np.zeros(size)
    else:
        if random_stream not in {"Global stream", "mt19937ar with seed"}:
            raise InputError("random_stream must be Global stream or mt19937ar with seed")
        if random_stream == "mt19937ar with seed":
            if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 2**32 - 1:
                raise InputError("seed must be an integer in 0..4294967295")
            rng = np.random.RandomState(seed)
            fading = stddev * rng.standard_normal(size)
        else:
            fading = stddev * np.random.standard_normal(size)
    return np.maximum(deterministic + fading + tx_gain + rx_gain - tx_loss - rx_loss, 0)


def _handler(_args, request):
    if "distance" not in request:
        raise InputError("distance is required")
    result = path_loss(request["distance"], **{key: value for key, value in request.items() if key != "distance"})
    return {"result": {"path_loss_db": result.tolist()}}


if __name__ == "__main__":
    run_cli("bluetooth_path_loss", _handler, description=__doc__)
