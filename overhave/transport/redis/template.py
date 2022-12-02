from functools import cached_property

import walrus

from overhave.transport.redis.deps import make_redis
from overhave.transport.redis.settings import BaseRedisSettings


class RedisTemplate:
    """Base class for :class:`RedisProducer` and :class:`RedisConsumer`."""

    def __init__(self, settings: BaseRedisSettings):
        self._settings = settings
        self._redis = make_redis(settings)

    @cached_property
    def _database(self) -> walrus.Database:
        return walrus.Database(connection_pool=self._redis.connection_pool)
