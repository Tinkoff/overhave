from functools import cached_property

import walrus

from overhave.entities.settings import OverhaveRedisSentinelSettings, OverhaveRedisSettings
from overhave.transport.redis.deps import make_redis


class RedisTemplate:
    """Base class for :class:`RedisProducer` and :class:`RedisConsumer`."""

    def __init__(self, settings: OverhaveRedisSettings, sentinel_settings: OverhaveRedisSentinelSettings):
        self._settings = settings
        self._redis = make_redis(settings, sentinel_settings)

    @cached_property
    def _database(self) -> walrus.Database:
        return walrus.Database(connection_pool=self._redis.connection_pool)
