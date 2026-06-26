import random

from pnwater.rivers import RIVERS_BY_ID
from pnwater.services.simulator.generator import generate_reading


def test_reading_has_all_fields_and_correct_river_id():
    river = RIVERS_BY_ID["cedar"]
    reading = generate_reading(river, random.Random(0))

    assert reading["river_id"] == "cedar"
    assert "recorded_at" in reading
    for param in ("temp_c", "dissolved_oxygen_mgl", "ph", "turbidity_fnu"):
        assert isinstance(reading[param], float)


def test_most_readings_stay_within_a_few_std_devs_of_baseline():
    river = RIVERS_BY_ID["white"]
    rng = random.Random(42)
    within_range = 0
    n = 500

    for _ in range(n):
        reading = generate_reading(river, rng)
        z = abs(reading["temp_c"] - river.temp_c.mean) / river.temp_c.std
        if z < 3.0:
            within_range += 1

    # ANOMALY_PROBABILITY is 3%, so the vast majority of ticks should be
    # within 3 std devs even allowing for ordinary Gaussian noise.
    assert within_range / n > 0.90
