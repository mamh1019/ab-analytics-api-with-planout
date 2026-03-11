#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import asyncio
from datetime import datetime
from aiokafka import AIOKafkaProducer
from typing import Optional
from decorators import handle_error_skip
from config.constants import KafkaMessage
from config import settings


class Kafka:
    _instance: Optional["Kafka"] = None
    _producer: Optional[AIOKafkaProducer] = None

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls) -> "Kafka":
        return cls._instance

    @handle_error_skip
    async def start(self, bootstrap_servers: str):
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                compression_type="gzip",
            )
            await self._producer.start()
            print("🚀 Kafka Producer Started")

    async def stop(self):
        if self._producer:
            await self._producer.stop()
            self._producer = None
            print("🛑 Kafka Producer Stopped")

    @handle_error_skip
    async def send(self, category: str, message: dict):
        if self._producer is None:
            raise RuntimeError("Kafka Producer is not started")

        """ 카프카에는 datetime 오브젝트를 전달 하면 안됩니다. 그렇다고 매 번 키를 체크 할 수 없으니 규약으로 하드코딩 합니다.
        """
        if "created_at" in message and isinstance(message["created_at"], datetime):
            message["created_at"] = message["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        if "updated_at" in message and isinstance(message["updated_at"], datetime):
            message["updated_at"] = message["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

        if settings.env != "prod":
            for _, v in message.items():
                if isinstance(v, datetime):
                    print("###################### Error #######################")
                    print("kafka 에는 datetime 타입을 전달 할 수 없습니다.")
                    print("######################################################")
                    return False

        payload = {"category": category, "data": message}
        try:
            return await asyncio.wait_for(
                self._producer.send_and_wait(KafkaMessage.AB_TEST_TOPIC, value=payload),
                timeout=2,
            )
        except asyncio.TimeoutError:
            raise RuntimeError("Kafka send timed out") from None
        except Exception as e:
            raise RuntimeError(f"Kafka send failed: {e}") from e
