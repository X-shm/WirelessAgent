"""Estimate Bluetooth range from link budget and propagation environment."""
from __future__ import annotations

import math
import numpy as np

from _bluetooth_common import InputError, run_cli
from bluetooth_path_loss import WAVELENGTH


def _number(request, name, default, *, lower=None, upper=None, strict_lower=False):
    value = request.get(name, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise InputError(f"{name} must be a finite number")
    value = float(value)
    if (lower is not None and (value <= lower if strict_lower else value < lower)) or (upper is not None and value > upper):
        raise InputError(f"{name} is outside its allowed range")
    return value


def estimate(request):
    environment = request.get("environment", "Outdoor")
    if environment not in {"Outdoor", "Industrial", "Home", "Office"}:
        raise InputError("environment must be Outdoor, Industrial, Home, or Office")
    power_type = request.get("signal_power_type", "ReceiverSensitivity")
    if power_type not in {"ReceiverSensitivity", "ReceivedSignalPower"}:
        raise InputError("signal_power_type must be ReceiverSensitivity or ReceivedSignalPower")
    mode = request.get("mode", "LE1M")
    upper_sensitivity = -75 if mode == "LE500K" else -82 if mode == "LE125K" else -70
    if mode not in {"LE1M", "LE2M", "LE500K", "LE125K", "BR", "EDR2M", "EDR3M"}:
        raise InputError("unsupported mode")
    sensitivity = _number(request, "receiver_sensitivity", -94, lower=-110, upper=upper_sensitivity)
    margin = _number(request, "link_margin", 15, lower=0)
    received = _number(request, "received_signal_power", -79, upper=0, strict_lower=True)
    tx_power = _number(request, "transmitter_power", 0, lower=-20, upper=20)
    tx_gain = _number(request, "transmitter_antenna_gain", 0, lower=-10, upper=10)
    rx_gain = _number(request, "receiver_antenna_gain", 0, lower=-10, upper=10)
    tx_loss = _number(request, "transmitter_cable_loss", 1.25, lower=0)
    rx_loss = _number(request, "receiver_cable_loss", 1.25, lower=0)
    rx_power = sensitivity + margin if power_type == "ReceiverSensitivity" else received
    path_loss = tx_power + tx_gain + rx_gain - tx_loss - rx_loss - rx_power
    if environment == "Industrial":
        exponent = _number(request, "path_loss_exponent", 2.2, lower=0, strict_lower=True)
        stddev = _number(request, "standard_deviation", 2.667, lower=0)
        result = [10 ** ((path_loss - 45.7 - 1.5 * stddev) / (10 * exponent)),
                  10 ** ((path_loss - 45.7 + 1.5 * stddev) / (10 * exponent))]
    elif environment in {"Home", "Office"}:
        if environment == "Home":
            p0, breakpoint, first_exp, second_exp, stddev = 12.5, 11.0, 4.2, 7.6, 3.0
        else:
            p0, breakpoint, first_exp, second_exp, stddev = 26.8, 10.0, 4.2, 8.7, 3.7
        threshold = p0 + 10 * first_exp * math.log10(breakpoint)
        if path_loss > threshold:
            result = [10 ** ((path_loss - p0 - 1.5 * stddev - 10 * first_exp * math.log10(breakpoint)) / (10 * second_exp)) * breakpoint,
                      10 ** ((path_loss - p0 + 1.5 * stddev - 10 * first_exp * math.log10(breakpoint)) / (10 * second_exp)) * breakpoint]
        else:
            result = [10 ** ((path_loss - p0 - 1.5 * stddev) / (10 * first_exp)),
                      10 ** ((path_loss - p0 + 1.5 * stddev) / (10 * first_exp))]
    else:
        tx_height = _number(request, "transmitter_antenna_height", 1, lower=0, strict_lower=True)
        rx_height = _number(request, "receiver_antenna_height", 1, lower=0, strict_lower=True)
        spread = 1.5 * 5 / 3
        fading = np.asarray([spread, -spread], dtype=float)
        linear = 10 ** ((path_loss - fading) / 10)
        breakpoint = 4 * tx_height * rx_height / WAVELENGTH
        k = WAVELENGTH ** 2 / (4 * math.pi) ** 2
        pl_breakpoint = 10 * math.log10(breakpoint ** 2 / k)
        if path_loss > pl_breakpoint:
            approximate = (linear * tx_height ** 2 * rx_height ** 2) ** 0.25
        else:
            approximate = np.sqrt(k * linear)
        minimum, maximum = float(approximate.min()), float(approximate.max())
        start = min(1.0, minimum) if maximum < 200 else minimum
        step = ((maximum - minimum) / 5 if maximum < 10 else
                1.0 if maximum < 200 else 2.0)
        stop = maximum + minimum
        distance = np.arange(start, stop + step * 1e-10, step)
        phi = np.arctan((tx_height + rx_height) / distance)
        los = np.sqrt((tx_height - rx_height) ** 2 + distance ** 2)
        reflected = np.sqrt((tx_height + rx_height) ** 2 + distance ** 2)
        gamma = (18 * np.sin(phi) - np.sqrt(18 - np.cos(phi) ** 2)) / (18 * np.sin(phi) + np.sqrt(18 - np.cos(phi) ** 2))
        inverse = ((WAVELENGTH / (4 * np.pi * los)) ** 2
                   + (WAVELENGTH / (4 * np.pi * reflected)) ** 2
                   * gamma * np.cos((reflected - los) * 2 * np.pi / WAVELENGTH))
        with np.errstate(divide="ignore", invalid="ignore"):
            losses = 10 * np.log10(1 / inverse)
        result = [float(distance[np.nanargmin(np.abs(losses - target))])
                  for target in path_loss - fading]
    return {"range_m": result, "path_loss_db": path_loss, "received_power_dbm": rx_power}


def _handler(_args, request):
    return {"result": estimate(request)}


if __name__ == "__main__":
    run_cli("bluetooth_range", _handler, description=__doc__)
