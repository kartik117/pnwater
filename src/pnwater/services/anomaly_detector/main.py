from __future__ import annotations

import asyncio
import logging

from prometheus_client import Counter, start_http_server

from pnwater.config import settings
from pnwater.messaging.kafka_client import KafkaEventConsumer, KafkaEventProducer
from pnwater.messaging.topics import Topics
from pnwater.services.anomaly_detector.detector import AnomalyDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anomalies_detected_total = Counter(
    "pnwater_anomalies_detected_total", "Anomalous readings flagged", ["river_id", "parameter"]
)


async def run() -> None:
    start_http_server(8000)

    detector = AnomalyDetector.load()
    producer = KafkaEventProducer(settings.kafka_bootstrap_servers)
    consumer = KafkaEventConsumer(
        (Topics.RIVER_READINGS,), settings.kafka_bootstrap_servers, group_id="anomaly-detector"
    )
    await producer.start()
    await consumer.start()

    logger.info("anomaly detector consuming %s", Topics.RIVER_READINGS)
    try:
        async for event in consumer:
            try:
                alert = detector.score(event["value"])
            except Exception:
                logger.exception("failed to score reading %s", event.get("key"))
                continue

            if alert is None:
                continue

            anomalies_detected_total.labels(river_id=alert.river_id, parameter=alert.parameter).inc()
            await producer.publish(
                Topics.RIVER_ALERTS,
                key=alert.river_id,
                value={
                    "river_id": alert.river_id,
                    "parameter": alert.parameter,
                    "value": alert.value,
                    "baseline_mean": alert.baseline_mean,
                    "z_score": alert.z_score,
                    "recorded_at": alert.recorded_at.isoformat(),
                },
            )
    finally:
        await consumer.stop()
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(run())
