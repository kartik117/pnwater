"""Thin wrappers around aiokafka -- same shape as the ones in pulsepay.
Kept duplicated rather than shared as a library across projects: it's
20 lines, and a shared internal package would be more ceremony than
the four copies it'd save.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any, Protocol

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)


class EventProducer(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def publish(self, topic: str, key: str, value: dict[str, Any]) -> None: ...


class EventConsumer(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def __aiter__(self) -> AsyncIterator[dict[str, Any]]: ...


class KafkaEventProducer:
    def __init__(self, bootstrap_servers: str) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8"),
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def publish(self, topic: str, key: str, value: dict[str, Any]) -> None:
        await self._producer.send_and_wait(topic, value=value, key=key)


class KafkaEventConsumer:
    def __init__(self, topics: tuple[str, ...], bootstrap_servers: str, group_id: str) -> None:
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )

    async def start(self) -> None:
        await self._consumer.start()

    async def stop(self) -> None:
        await self._consumer.stop()

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        async for record in self._consumer:
            yield {"topic": record.topic, "key": record.key, "value": record.value}
