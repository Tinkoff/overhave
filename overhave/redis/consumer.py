import logging
from functools import cached_property
from types import TracebackType
from typing import Iterator, List, Sequence, Type

import walrus

from overhave.entities.settings import OverhaveRedisSettings
from overhave.redis.objects import RedisPendingData, RedisStream, RedisUnreadData
from overhave.redis.template import RedisTemplate

logger = logging.getLogger(__name__)


class RedisConsumer(RedisTemplate):
    """ Class for consuming tasks from Redis stream ```stream_name```. """

    def __init__(self, settings: OverhaveRedisSettings, stream_name: RedisStream):
        super().__init__(settings)
        self._stream_name = stream_name

    @cached_property
    def _consumer_group(self) -> walrus.ConsumerGroup:
        consumer_group = self._database.consumer_group(f"cg-{self._stream_name}", (self._stream_name,))
        consumer_group.create()
        return consumer_group

    @property
    def _stream(self) -> walrus.containers.ConsumerGroupStream:
        return getattr(self._consumer_group, self._stream_name.with_dunder)

    def _clean_pending(self) -> None:
        pending_messages = self._stream.pending()
        models: List[RedisPendingData] = [RedisPendingData.parse_obj(msg) for msg in pending_messages]
        if models:
            message_ids = [x.message_id for x in models]
            self._stream.claim(*message_ids)
            self._stream.ack(*message_ids)
            logger.info("Clean all pending messages for stream %s: %s", self._stream_name, models)

    def _consume(self) -> Sequence[RedisUnreadData]:
        messages = self._stream.read(count=self._settings.redis_read_count, block=self._settings.timeout_milliseconds)
        objects: List[RedisUnreadData] = []
        for msg in messages:
            data = RedisUnreadData(*msg)
            logger.info("Message from redis: %s", data)
            self._stream.ack(data.message_id)
            objects.append(data)
        return objects

    def __enter__(self) -> None:
        logger.info("Starting consuming from %s...", self._stream_name)
        self._clean_pending()

    def __iter__(self) -> Iterator[Sequence[RedisUnreadData]]:
        while True:
            try:
                logger.debug("Check messages...")
                messages = self._consume()
                if messages:
                    logger.debug("Has messages, return them")
                    yield messages
                continue
            except Exception:
                logger.exception("Error while trying to consume message from redis!")
            raise StopIteration()

    def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: TracebackType) -> None:
        pass
