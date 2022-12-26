import logging

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from pytest_redis import factories
from redis import Redis, Sentinel

from overhave.factory import ConsumerFactory
from overhave.transport import (
    BaseRedisSettings,
    OverhaveRedisSentinelSettings,
    OverhaveRedisSettings,
    RedisProducer,
    RedisStream,
    TestRunTask,
)

logger = logging.getLogger(__name__)

_REDIS_DB_NUM = 1
redisdb = factories.redisdb("redis_nooproc", dbnum=_REDIS_DB_NUM)


@pytest.fixture()
def enable_sentinel(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def default_redis_settings(faker: Faker) -> OverhaveRedisSettings:
    return OverhaveRedisSettings(db=_REDIS_DB_NUM)


@pytest.fixture()
def sentinel_redis_settings(faker: Faker) -> OverhaveRedisSentinelSettings:
    return OverhaveRedisSentinelSettings(db=_REDIS_DB_NUM, master_set=faker.word(), password=faker.word())


@pytest.fixture()
def redis_settings(
    enable_sentinel: bool,
    default_redis_settings: OverhaveRedisSettings,
    sentinel_redis_settings: OverhaveRedisSentinelSettings,
) -> BaseRedisSettings:
    if enable_sentinel:
        return sentinel_redis_settings
    return default_redis_settings


@pytest.fixture()
def mock_sentinel(redis_settings: BaseRedisSettings) -> None:
    if not isinstance(redis_settings, OverhaveRedisSentinelSettings):
        return
    Sentinel.master_for = lambda *args, **kwargs: Redis.from_url(
        str(redis_settings.urls[0]),
        db=redis_settings.db,
        socket_timeout=redis_settings.socket_timeout.total_seconds(),
    )


@pytest.fixture()
def redis_producer(redis_settings: BaseRedisSettings, mock_sentinel: None) -> RedisProducer:
    return RedisProducer(settings=redis_settings, mapping={TestRunTask: RedisStream.TEST})


@pytest.fixture()
def redis_consumer_factory(redis_settings: BaseRedisSettings, mock_sentinel: None) -> ConsumerFactory:
    factory = ConsumerFactory(stream=RedisStream.TEST)
    factory._redis_settings = redis_settings
    logger.info("Setup %s to consumer factory instance", factory._redis_settings)
    return factory


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.random_int()
