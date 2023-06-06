import logging
from functools import cache

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
from overhave.transport.redis.deps import get_redis_settings

logger = logging.getLogger(__name__)


@cache
def _get_initial_redis_settings() -> OverhaveRedisSettings:
    """Cached function for get params from environment in tests."""
    return OverhaveRedisSettings(db=15)  # for exclusion of intersections with other test configs


@pytest.fixture(scope="module")
def envs_for_mock() -> dict[str, str | None]:
    return {
        "OVERHAVE_REDIS_DB": f"{_get_initial_redis_settings().db}",
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


redis_external = factories.redis_noproc(
    host=_get_initial_redis_settings().url.host,
    port=_get_initial_redis_settings().url.port,
)
redisdb = factories.redisdb("redis_external", dbnum=_get_initial_redis_settings().db)


@pytest.fixture()
def enable_sentinel(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def default_redis_settings(faker: Faker) -> OverhaveRedisSettings:
    return OverhaveRedisSettings(db=_get_initial_redis_settings().db)


@pytest.fixture()
def sentinel_redis_settings(faker: Faker) -> OverhaveRedisSentinelSettings:
    return OverhaveRedisSentinelSettings(db=_get_initial_redis_settings().db)


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
def clear_redis_settings(redis_settings: BaseRedisSettings) -> None:
    get_redis_settings.cache_clear()


@pytest.fixture()
def redis_consumer_factory(
    mock_envs: None,
    redis_settings: BaseRedisSettings,
    mock_sentinel: None,
    clear_redis_settings: None,
) -> ConsumerFactory:
    return ConsumerFactory(stream=RedisStream.TEST)


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.random_int()
