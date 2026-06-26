from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import joblib

from pnwater.ml.features import PARAMETERS, feature_vector, z_scores
from pnwater.ml.train import MODEL_PATH
from pnwater.models.schemas import AnomalyAlert
from pnwater.rivers import RIVERS_BY_ID


class AnomalyDetector:
    """Wraps the trained XGBoost classifier. Takes a raw reading dict
    (river_id, recorded_at ISO string, four parameter values) and
    returns an AnomalyAlert for the single most-deviant parameter, or
    None if the model doesn't flag the reading.

    Model is injected so tests can pass a stub instead of loading the
    real joblib artifact from disk.
    """

    def __init__(self, model: Any) -> None:
        self._model = model

    @classmethod
    def load(cls, model_path: Path = MODEL_PATH) -> AnomalyDetector:
        return cls(joblib.load(model_path))

    def score(self, reading: dict) -> AnomalyAlert | None:
        river = RIVERS_BY_ID[reading["river_id"]]
        features = feature_vector(reading, river)

        is_anomaly = bool(self._model.predict([features])[0])
        if not is_anomaly:
            return None

        z = z_scores(reading, river)
        worst_param = max(PARAMETERS, key=lambda p: abs(z[p]))

        return AnomalyAlert(
            river_id=river.id,
            parameter=worst_param,
            value=reading[worst_param],
            baseline_mean=getattr(river, worst_param).mean,
            z_score=z[worst_param],
            recorded_at=datetime.fromisoformat(reading["recorded_at"]),
        )
