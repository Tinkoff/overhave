import pytest
from faker import Faker
from pytest_redis import factories

from overhave.entities.settings import OverhaveRedisSettings
from overhave.factory import ConsumerFactory
from overhave.transport import RedisProducer, RedisStream, TestRunTask

redis_proc = factories.redis_proc(port="6379")
redisdb = factories.redisdb("redis_proc", dbnum=1)


@pytest.fixture()
def redis_consumer_factory() -> ConsumerFactory:
    return ConsumerFactory(stream=RedisStream.TEST)


@pytest.fixture()
def redis_settings() -> OverhaveRedisSettings:
    return OverhaveRedisSettings()


@pytest.fixture()
def redis_producer(redis_settings: OverhaveRedisSettings) -> RedisProducer:
    return RedisProducer(settings=redis_settings, mapping={TestRunTask: RedisStream.TEST})


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.random_int()
