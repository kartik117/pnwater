from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Reading(BaseModel):
    river_id: str
    recorded_at: datetime
    temp_c: float
    dissolved_oxygen_mgl: float
    ph: float
    turbidity_fnu: float


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyAlert(BaseModel):
    river_id: str
    parameter: str
    value: float
    baseline_mean: float
    z_score: float
    recorded_at: datetime
