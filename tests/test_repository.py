from datetime import datetime, timezone

from pnwater.storage.repository import AlertRepository, ReadingRepository


def test_latest_for_river_returns_most_recent(session_factory):
    with session_factory() as session:
        repo = ReadingRepository(session)
        repo.create(
            river_id="cedar", recorded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            temp_c=10.0, dissolved_oxygen_mgl=10.0, ph=7.5, turbidity_fnu=1.0,
        )
        repo.create(
            river_id="cedar", recorded_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            temp_c=11.0, dissolved_oxygen_mgl=10.0, ph=7.5, turbidity_fnu=1.0,
        )

    with session_factory() as session:
        latest = ReadingRepository(session).latest_for_river("cedar")
        assert latest.temp_c == 11.0


def test_latest_all_skips_rivers_with_no_readings(session_factory):
    with session_factory() as session:
        ReadingRepository(session).create(
            river_id="cedar", recorded_at=datetime.now(timezone.utc),
            temp_c=10.0, dissolved_oxygen_mgl=10.0, ph=7.5, turbidity_fnu=1.0,
        )

    with session_factory() as session:
        rows = ReadingRepository(session).latest_all()
        assert len(rows) == 1
        assert rows[0].river_id == "cedar"


def test_alert_repository_recent_orders_newest_first(session_factory):
    with session_factory() as session:
        repo = AlertRepository(session)
        repo.create(
            river_id="yakima", parameter="temp_c", value=30.0, baseline_mean=23.2, z_score=3.0,
            severity="warning", message="older", recorded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        repo.create(
            river_id="yakima", parameter="temp_c", value=35.0, baseline_mean=23.2, z_score=5.0,
            severity="critical", message="newer", recorded_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )

    with session_factory() as session:
        rows = AlertRepository(session).recent(limit=10)
        assert [r.message for r in rows] == ["newer", "older"]
