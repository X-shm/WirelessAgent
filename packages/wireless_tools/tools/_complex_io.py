"""JSON helpers shared by complex-valued command-line tools."""
from __future__ import annotations
import json
import numpy as np


def parse_complex(text: str) -> np.ndarray:
    value = json.loads(text)
    if isinstance(value, dict):
        real = np.asarray(value.get("real", []), dtype=float)
        imag = np.asarray(value.get("imag", np.zeros_like(real)), dtype=float)
        if real.shape != imag.shape:
            raise ValueError("real and imag arrays must have the same shape")
        return real + 1j * imag
    return np.asarray(value, dtype=float).astype(complex)


def complex_json(values) -> dict:
    array = np.asarray(values)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}
