from datetime import datetime, timezone

import pytest

from pnwater.services.anomaly_detector.detector import AnomalyDetector


class _StubModel:
    """Always predicts whatever it's constructed with -- isolates the
    detector's wiring (feature extraction, worst-parameter selection,
    alert construction) from whether the real classifier is right.
    """

    def __init__(self, prediction: int) -> None:
        self._prediction = prediction

    def predict(self, X):
        return [self._prediction]


def _reading(river_id="white", **overrides):
    base = {
        "river_id": river_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "temp_c": 9.4,
        "dissolved_oxygen_mgl": 10.6,
        "ph": 7.4,
        "turbidity_fnu": 1.4,
    }
    base.update(overrides)
    return base


def test_normal_prediction_returns_none():
    detector = AnomalyDetector(_StubModel(prediction=0))
    assert detector.score(_reading()) is None


def test_anomalous_prediction_returns_alert_for_worst_parameter():
    detector = AnomalyDetector(_StubModel(prediction=1))
    reading = _reading(temp_c=9.4 + 6 * 1.2)  # white river temp_c std is 1.2

    alert = detector.score(reading)

    assert alert is not None
    assert alert.river_id == "white"
    assert alert.parameter == "temp_c"
    assert alert.z_score == pytest.approx(6.0)


def test_picks_the_most_deviant_parameter_not_just_the_first():
    detector = AnomalyDetector(_StubModel(prediction=1))
    # ph deviates by 2 std devs, turbidity by 5 -- turbidity should win.
    reading = _reading(ph=7.4 + 2 * 0.2, turbidity_fnu=1.4 + 5 * 1.0)

    alert = detector.score(reading)

    assert alert.parameter == "turbidity_fnu"


def test_real_trained_model_flags_an_extreme_reading_and_clears_a_normal_one():
    detector = AnomalyDetector.load()

    normal = _reading()
    extreme = _reading(temp_c=9.4 + 7 * 1.2, turbidity_fnu=1.4 + 6 * 1.0)

    assert detector.score(normal) is None
    alert = detector.score(extreme)
    assert alert is not None
    assert alert.river_id == "white"
