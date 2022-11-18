import pytest
from overhave.entities.settings import OverhaveRedisSettings
from overhave.transport import RedisProducer, RedisStream, TestRunTask, RedisConsumer, RedisConsumerRunner
from overhave.factory import ConsumerFactory
from faker import Faker


@pytest.fixture()
def redis_consumer() -> RedisConsumer:
    return RedisConsumer(settings=OverhaveRedisSettings(), stream_name=RedisStream.TEST)


@pytest.fixture()
def redis_producer() -> RedisProducer:
    return RedisProducer(settings=OverhaveRedisSettings(), mapping={TestRunTask: RedisStream.TEST})


@pytest.fixture()
def run_id(faker: Faker) -> int:
    return faker.pyint()


@pytest.fixture()
def redis_runner(redis_consumer: RedisConsumer) -> RedisConsumerRunner:
    return ConsumerFactory(stream=RedisStream.TEST).runner
