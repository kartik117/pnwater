from datetime import datetime, timezone

from pnwater.services.ingest.main import persist_reading
from pnwater.storage.repository import ReadingRepository


def test_persist_reading_writes_a_row(monkeypatch, session_factory):
    monkeypatch.setattr("pnwater.services.ingest.main.SessionLocal", session_factory)

    value = {
        "river_id": "tolt",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "temp_c": 11.2,
        "dissolved_oxygen_mgl": 10.0,
        "ph": 7.6,
        "turbidity_fnu": 0.6,
    }
    persist_reading(value)

    with session_factory() as session:
        row = ReadingRepository(session).latest_for_river("tolt")
        assert row is not None
        assert row.temp_c == 11.2
