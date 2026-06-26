"""Generates one synthetic reading per river per tick.

Gaussian noise around each river's real-calibrated baseline, plus a
small random chance of injecting a sensor anomaly -- this is the one
place in the system that knows whether a reading is *supposed* to be
anomalous, which is deliberately thrown away before publishing (the
anomaly_detector has to find it from the value alone, the same way it
would have to for a real sensor fault).
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from pnwater.ml.features import PARAMETERS
from pnwater.rivers import River

ANOMALY_PROBABILITY = 0.03


def generate_reading(river: River, rng: random.Random) -> dict[str, float | str]:
    values = {p: rng.gauss(getattr(river, p).mean, getattr(river, p).std) for p in PARAMETERS}

    if rng.random() < ANOMALY_PROBABILITY:
        param = rng.choice(PARAMETERS)
        baseline = getattr(river, param)
        magnitude = rng.uniform(4.0, 8.0) * rng.choice([-1, 1])
        values[param] = baseline.mean + magnitude * baseline.std

    return {
        "river_id": river.id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **values,
    }
