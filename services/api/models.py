"""Versioned public request contract for the first simulation task."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


DEFAULT_DISTANCES = [1.0, 5.0, 10.0, 25.0, 50.0, 100.0]


class BlePowerDistanceParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tx_power_dbm: float = Field(default=0.0, ge=-20, le=20)
    receiver_sensitivity_dbm: float = Field(default=-75.0, ge=-110, le=-70)
    distances_m: list[float] = Field(default_factory=lambda: list(DEFAULT_DISTANCES), min_length=2, max_length=20)
    packets_per_distance: int = Field(default=20, ge=1, le=100)

    @field_validator("distances_m")
    @classmethod
    def check_distances(cls, values: list[float]) -> list[float]:
        if not all(math.isfinite(value) for value in values):
            raise ValueError("distances must be finite")
        if any(value < 1 or value > 1000 for value in values):
            raise ValueError("each distance must be between 1 and 1000 metres")
        if any(right <= left for left, right in zip(values, values[1:])):
            raise ValueError("distances must be strictly increasing")
        return values


class CreateSimulationTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["ble_power_distance_v1"]
    parameters: BlePowerDistanceParameters = Field(default_factory=BlePowerDistanceParameters)
