from datetime import datetime, timezone

import pnwater.services.api.main as api_main
from fastapi.testclient import TestClient


def test_health():
    client = TestClient(api_main.app)
    assert client.get("/health").json() == {"status": "ok"}


def test_list_rivers_returns_all_ten():
    client = TestClient(api_main.app)
    response = client.get("/rivers")
    assert response.status_code == 200
    assert len(response.json()) == 10
    assert {r["id"] for r in response.json()} >= {"cedar", "yakima", "columbia"}


def test_latest_readings_reflects_seeded_data(monkeypatch, session_factory):
    monkeypatch.setattr(api_main, "SessionLocal", session_factory)
    from pnwater.storage.repository import ReadingRepository

    with session_factory() as session:
        ReadingRepository(session).create(
            river_id="cedar", recorded_at=datetime.now(timezone.utc),
            temp_c=10.7, dissolved_oxygen_mgl=10.0, ph=7.6, turbidity_fnu=1.8,
        )

    client = TestClient(api_main.app)
    response = client.get("/readings/latest")
    assert response.status_code == 200
    assert any(r["river_id"] == "cedar" for r in response.json())


def test_recent_alerts_reflects_seeded_data(monkeypatch, session_factory):
    monkeypatch.setattr(api_main, "SessionLocal", session_factory)
    from pnwater.storage.repository import AlertRepository

    with session_factory() as session:
        AlertRepository(session).create(
            river_id="yakima", parameter="temp_c", value=35.0, baseline_mean=23.2, z_score=4.7,
            severity="critical", message="test alert", recorded_at=datetime.now(timezone.utc),
        )

    client = TestClient(api_main.app)
    response = client.get("/alerts/recent")
    assert response.status_code == 200
    assert response.json()[0]["message"] == "test alert"
