import pytest
from redis.client import Redis

from overhave.factory import ConsumerFactory
from overhave.transport import RedisProducer, RedisStream, TestRunData, TestRunTask


class TestRedisConsumerAndProducer:
    """Unit tests for :class:`RedisConsumer` and :class:`RedisProducer`."""

    def test_consumer_group(
        self,
        redis_consumer_factory: ConsumerFactory,
        redisdb: Redis,  # type: ignore
    ) -> None:
        redis_consumer = redis_consumer_factory._consumer
        consumer_group = redis_consumer._consumer_group
        assert consumer_group.keys.get(RedisStream.TEST)

    @pytest.mark.parametrize("enable_sentinel", [True, False], indirect=True)
    def test_consume_new(
        self,
        redis_consumer_factory: ConsumerFactory,
        redis_producer: RedisProducer,
        run_id: int,
        redisdb: Redis,  # type: ignore
        mock_sentinel: None,
    ) -> None:
        redis_consumer = redis_consumer_factory._consumer
        task = TestRunTask(data=TestRunData(test_run_id=run_id))
        assert redis_producer.add_task(task)
        task_from_consumer = redis_consumer._consume()[-1]
        run_id_from_task = task_from_consumer.decoded_message["data"]["test_run_id"]
        assert run_id_from_task == run_id
