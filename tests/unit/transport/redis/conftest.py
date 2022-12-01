import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from pytest_redis import factories

from overhave.factory import ConsumerFactory
from overhave.transport import (
    BaseRedisSettings,
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
def redis_settings(faker: Faker, enable_sentinel: bool) -> BaseRedisSettings:
    if enable_sentinel:
        return OverhaveRedisSentinelSettings(master_set=faker.word(), redis_password=faker.word())
    return OverhaveRedisSettings()


@pytest.fixture()
def redis_producer(redis_settings: BaseRedisSettings) -> RedisProducer:
    return RedisProducer(settings=redis_settings, mapping={TestRunTask: RedisStream.TEST})


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.random_int()
