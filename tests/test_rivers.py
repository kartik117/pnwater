from pnwater.rivers import RIVERS, RIVERS_BY_ID


def test_ten_distinct_rivers():
    assert len(RIVERS) == 10
    assert len({r.id for r in RIVERS}) == 10


def test_every_river_has_positive_std_for_every_parameter():
    for river in RIVERS:
        for param in ("temp_c", "dissolved_oxygen_mgl", "ph", "turbidity_fnu"):
            baseline = getattr(river, param)
            assert baseline.std > 0, f"{river.id}.{param} has non-positive std"


def test_rivers_by_id_matches_rivers():
    assert set(RIVERS_BY_ID) == {r.id for r in RIVERS}
    for river in RIVERS:
        assert RIVERS_BY_ID[river.id] is river
