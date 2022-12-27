import logging
from functools import cache

from redis import Redis
from redis.sentinel import Sentinel

from overhave.transport.redis.settings import BaseRedisSettings, OverhaveRedisSentinelSettings, OverhaveRedisSettings

logger = logging.getLogger(__name__)


def make_sentinel_master(settings: OverhaveRedisSentinelSettings) -> Redis:  # type: ignore
    logger.info("Connecting to redis through sentinel %s", settings.urls)
    url_tuples = [(url.host, url.port) for url in settings.urls if url.host is not None and url.port is not None]
    sentinel = Sentinel(url_tuples, socket_timeout=settings.socket_timeout.total_seconds(), retry_on_timeout=True)
    return sentinel.master_for(settings.master_set, password=settings.password, db=settings.db)


def make_regular_redis(redis_settings: OverhaveRedisSettings) -> Redis:  # type: ignore
    return Redis.from_url(
        str(redis_settings.url),
        db=redis_settings.db,
        socket_timeout=redis_settings.socket_timeout.total_seconds(),
    )


def make_redis(redis_settings: BaseRedisSettings) -> Redis:  # type: ignore  # noqa: E501
    if isinstance(redis_settings, OverhaveRedisSentinelSettings):
        return make_sentinel_master(redis_settings)

    if isinstance(redis_settings, OverhaveRedisSettings):
        return make_regular_redis(redis_settings)

    raise RuntimeError("redis_settings is not any instance of OverhaveRedisSentinelSettings, OverhaveRedisSettings")


@cache
def get_redis_settings() -> BaseRedisSettings:
    sentinel_settings = OverhaveRedisSentinelSettings()
    if sentinel_settings.enabled:
        return sentinel_settings
    return OverhaveRedisSettings()
