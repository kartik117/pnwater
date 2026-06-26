from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from prometheus_client import Counter, start_http_server

from pnwater.config import settings
from pnwater.messaging.kafka_client import KafkaEventConsumer
from pnwater.messaging.topics import Topics
from pnwater.services.alert_agent.graph import build_graph
from pnwater.storage.db import SessionLocal
from pnwater.storage.repository import AlertRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

alerts_recorded_total = Counter(
    "pnwater_alerts_recorded_total", "Alerts recorded after the LangGraph pipeline", ["severity"]
)


async def run() -> None:
    start_http_server(8000)

    graph = build_graph()
    consumer = KafkaEventConsumer(
        (Topics.RIVER_ALERTS,), settings.kafka_bootstrap_servers, group_id="alert-agent"
    )
    await consumer.start()

    logger.info("alert agent consuming %s", Topics.RIVER_ALERTS)
    try:
        async for event in consumer:
            try:
                value = event["value"]
                result = await graph.ainvoke(
                    {
                        "river_id": value["river_id"],
                        "parameter": value["parameter"],
                        "value": value["value"],
                        "baseline_mean": value["baseline_mean"],
                        "z_score": value["z_score"],
                        "severity": "",
                        "message": "",
                    }
                )
                with SessionLocal() as session:
                    AlertRepository(session).create(
                        river_id=result["river_id"],
                        parameter=result["parameter"],
                        value=result["value"],
                        baseline_mean=result["baseline_mean"],
                        z_score=result["z_score"],
                        severity=result["severity"],
                        message=result["message"],
                        recorded_at=datetime.fromisoformat(value["recorded_at"]),
                    )
                alerts_recorded_total.labels(severity=result["severity"]).inc()
                logger.info(result["message"])
            except Exception:
                logger.exception("failed to process alert %s", event.get("key"))
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run())
