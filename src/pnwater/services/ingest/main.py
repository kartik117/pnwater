from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from prometheus_client import start_http_server

from pnwater.config import settings
from pnwater.messaging.kafka_client import KafkaEventConsumer
from pnwater.messaging.topics import Topics
from pnwater.storage.db import SessionLocal
from pnwater.storage.repository import ReadingRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def persist_reading(value: dict) -> None:
    with SessionLocal() as session:
        ReadingRepository(session).create(
            river_id=value["river_id"],
            recorded_at=datetime.fromisoformat(value["recorded_at"]),
            temp_c=value["temp_c"],
            dissolved_oxygen_mgl=value["dissolved_oxygen_mgl"],
            ph=value["ph"],
            turbidity_fnu=value["turbidity_fnu"],
        )


async def run() -> None:
    start_http_server(8000)

    consumer = KafkaEventConsumer(
        (Topics.RIVER_READINGS,), settings.kafka_bootstrap_servers, group_id="ingest-service"
    )
    await consumer.start()

    logger.info("ingest service consuming %s", Topics.RIVER_READINGS)
    try:
        async for event in consumer:
            try:
                persist_reading(event["value"])
            except Exception:
                logger.exception("failed to persist reading %s", event.get("key"))
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run())
