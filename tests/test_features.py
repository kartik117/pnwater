from pnwater.ml.features import feature_vector, z_scores
from pnwater.rivers import RIVERS_BY_ID


def test_z_score_is_zero_at_baseline_mean():
    river = RIVERS_BY_ID["yakima"]
    reading = {
        "temp_c": river.temp_c.mean,
        "dissolved_oxygen_mgl": river.dissolved_oxygen_mgl.mean,
        "ph": river.ph.mean,
        "turbidity_fnu": river.turbidity_fnu.mean,
    }
    z = z_scores(reading, river)
    assert all(abs(v) < 1e-9 for v in z.values())


def test_z_score_scales_with_std():
    river = RIVERS_BY_ID["columbia"]
    reading = {
        "temp_c": river.temp_c.mean + 2 * river.temp_c.std,
        "dissolved_oxygen_mgl": river.dissolved_oxygen_mgl.mean,
        "ph": river.ph.mean,
        "turbidity_fnu": river.turbidity_fnu.mean,
    }
    z = z_scores(reading, river)
    assert z["temp_c"] == 2.0


def test_same_absolute_temperature_is_normal_for_one_river_and_anomalous_for_another():
    # 23degC is Yakima's baseline; it's far above Columbia's ~10degC baseline.
    yakima = RIVERS_BY_ID["yakima"]
    columbia = RIVERS_BY_ID["columbia"]
    reading = {"temp_c": 23.0, "dissolved_oxygen_mgl": 0, "ph": 0, "turbidity_fnu": 0}

    yakima_z = z_scores(reading, yakima)["temp_c"]
    columbia_z = z_scores(reading, columbia)["temp_c"]

    assert abs(yakima_z) < 1.0
    assert abs(columbia_z) > 5.0


def test_feature_vector_order_matches_parameters():
    river = RIVERS_BY_ID["white"]
    reading = {"temp_c": 9.4, "dissolved_oxygen_mgl": 10.6, "ph": 7.4, "turbidity_fnu": 1.4}
    vec = feature_vector(reading, river)
    assert len(vec) == 4
    assert all(abs(v) < 1e-9 for v in vec)
