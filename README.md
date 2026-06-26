# PNWater

Real-time water quality monitoring for Pacific Northwest rivers. Simulated IoT sensors at 10 river locations stream readings through Kafka into TimescaleDB; an XGBoost model calibrated on USGS data flags anomalies, and a LangGraph agent turns flagged events into plain-language alerts.

## Planned architecture

```
Simulated sensors (10 rivers) -> Kafka -> TimescaleDB
                                              |
                                              v
                                   XGBoost anomaly detection
                                              |
                                              v
                                   LangGraph alert agent -> Next.js + Mapbox dashboard
```

## Planned stack

Kafka (Docker) · TimescaleDB · XGBoost + scikit-learn · LangGraph · FastAPI · Next.js + Mapbox GL JS · USGS Water Quality API

## Status

Planned — design complete, scaffolding in progress.
