import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from pytest_redis import factories

from overhave.factory import ConsumerFactory
from overhave.transport import (
    OverhaveRedisSentinelSettings,
    OverhaveRedisSettings,
    RedisProducer,
    RedisStream,
    TestRunTask,
)

redis_proc = factories.redis_proc(port="6379")
redisdb = factories.redisdb("redis_proc", dbnum=1)


@pytest.fixture()
def enable_sentinel(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def redis_consumer_factory() -> ConsumerFactory:
    return ConsumerFactory(stream=RedisStream.TEST)


@pytest.fixture()
def redis_settings() -> OverhaveRedisSettings:
    return OverhaveRedisSettings()


@pytest.fixture()
def redis_sentinel_settings(faker: Faker, enable_sentinel: bool) -> OverhaveRedisSentinelSettings:
    return OverhaveRedisSentinelSettings(enabled=enable_sentinel, master_set=faker.word(), redis_password=faker.word())


@pytest.fixture()
def redis_producer(
    redis_settings: OverhaveRedisSettings, redis_sentinel_settings: redis_sentinel_settings
) -> RedisProducer:
    return RedisProducer(
        settings=redis_settings, mapping={TestRunTask: RedisStream.TEST}, sentinel_settings=redis_sentinel_settings
    )


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.random_int()
