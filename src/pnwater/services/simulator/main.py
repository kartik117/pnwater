from __future__ import annotations

import asyncio
import logging
import random

from prometheus_client import Counter, start_http_server

from pnwater.config import settings
from pnwater.messaging.kafka_client import KafkaEventProducer
from pnwater.messaging.topics import Topics
from pnwater.rivers import RIVERS
from pnwater.services.simulator.generator import generate_reading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

readings_published_total = Counter(
    "pnwater_readings_published_total", "Synthetic readings published", ["river_id"]
)


async def run() -> None:
    start_http_server(8000)
    rng = random.Random()

    producer = KafkaEventProducer(settings.kafka_bootstrap_servers)
    await producer.start()

    logger.info("simulator publishing for %d rivers every %ss", len(RIVERS), settings.simulator_interval_seconds)
    try:
        while True:
            for river in RIVERS:
                reading = generate_reading(river, rng)
                await producer.publish(Topics.RIVER_READINGS, key=river.id, value=reading)
                readings_published_total.labels(river_id=river.id).inc()
            await asyncio.sleep(settings.simulator_interval_seconds)
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(run())
