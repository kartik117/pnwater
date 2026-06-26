"""Feature engineering for the anomaly classifier.

A river's "normal" is relative to itself: Yakima River runs warm
(baseline ~23degC) and Columbia River runs cold (~10degC) -- a single
global model trained on raw values would learn "high temperature is
anomalous" and flag every normal Yakima reading. Converting each
parameter to a z-score against *that river's own* baseline before
training means one model generalizes across all 10 rivers instead of
needing one model per river.
"""

from __future__ import annotations

from pnwater.rivers import River

PARAMETERS = ("temp_c", "dissolved_oxygen_mgl", "ph", "turbidity_fnu")


def z_scores(reading: dict[str, float], river: River) -> dict[str, float]:
    return {
        param: (reading[param] - getattr(river, param).mean) / getattr(river, param).std
        for param in PARAMETERS
    }


def feature_vector(reading: dict[str, float], river: River) -> list[float]:
    z = z_scores(reading, river)
    return [z[param] for param in PARAMETERS]
