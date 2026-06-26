from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from pnwater.rivers import RIVERS
from pnwater.storage.db import SessionLocal
from pnwater.storage.repository import AlertRepository, ReadingRepository

app = FastAPI(title="pnwater-api")
app.mount("/metrics", make_asgi_app())


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/rivers")
async def list_rivers() -> list[dict]:
    return [
        {"id": r.id, "name": r.name, "usgs_site": r.usgs_site, "lat": r.lat, "lon": r.lon}
        for r in RIVERS
    ]


@app.get("/readings/latest")
async def latest_readings() -> list[dict]:
    with SessionLocal() as session:
        rows = ReadingRepository(session).latest_all()
        return [
            {
                "river_id": row.river_id,
                "recorded_at": row.recorded_at.isoformat(),
                "temp_c": row.temp_c,
                "dissolved_oxygen_mgl": row.dissolved_oxygen_mgl,
                "ph": row.ph,
                "turbidity_fnu": row.turbidity_fnu,
            }
            for row in rows
        ]


@app.get("/alerts/recent")
async def recent_alerts(limit: int = 50) -> list[dict]:
    with SessionLocal() as session:
        rows = AlertRepository(session).recent(limit=limit)
        return [
            {
                "river_id": row.river_id,
                "parameter": row.parameter,
                "value": row.value,
                "baseline_mean": row.baseline_mean,
                "z_score": row.z_score,
                "severity": row.severity,
                "message": row.message,
                "recorded_at": row.recorded_at.isoformat(),
            }
            for row in rows
        ]
