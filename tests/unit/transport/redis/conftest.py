import pytest
from faker import Faker

from overhave.entities.settings import OverhaveRedisSettings
from overhave.factory import ConsumerFactory
from overhave.transport import RedisProducer, RedisStream, TestRunTask


@pytest.fixture()
def redis_consumer_factory() -> ConsumerFactory:
    return ConsumerFactory(stream=RedisStream.TEST)


@pytest.fixture()
def redis_producer() -> RedisProducer:
    return RedisProducer(settings=OverhaveRedisSettings(), mapping={TestRunTask: RedisStream.TEST})


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.random_int()
