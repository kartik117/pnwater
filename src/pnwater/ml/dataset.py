"""Synthetic training data, generated from the same real-calibrated
baselines the simulator uses -- not a separate invented distribution.

Anomalies perturb 1-2 randomly chosen parameters by 4-8 standard
deviations (sign random), modeling both a single failed sensor and a
real event (e.g. a temperature spike or a turbidity event from runoff)
that moves more than one reading at once.
"""

from __future__ import annotations

import random

from pnwater.ml.features import PARAMETERS, feature_vector
from pnwater.rivers import RIVERS, River


def _sample_normal(river: River, rng: random.Random) -> dict[str, float]:
    return {p: rng.gauss(getattr(river, p).mean, getattr(river, p).std) for p in PARAMETERS}


def _sample_anomalous(river: River, rng: random.Random) -> dict[str, float]:
    reading = _sample_normal(river, rng)
    affected = rng.sample(PARAMETERS, rng.choice([1, 2]))
    for param in affected:
        baseline = getattr(river, param)
        magnitude = rng.uniform(4.0, 8.0) * rng.choice([-1, 1])
        reading[param] = baseline.mean + magnitude * baseline.std
    return reading


def generate_dataset(
    n_normal_per_river: int = 300, n_anomalous_per_river: int = 60, seed: int = 42
) -> tuple[list[list[float]], list[int]]:
    rng = random.Random(seed)
    X: list[list[float]] = []
    y: list[int] = []

    for river in RIVERS:
        for _ in range(n_normal_per_river):
            X.append(feature_vector(_sample_normal(river, rng), river))
            y.append(0)
        for _ in range(n_anomalous_per_river):
            X.append(feature_vector(_sample_anomalous(river, rng), river))
            y.append(1)

    return X, y
