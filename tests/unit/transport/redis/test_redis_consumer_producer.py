from overhave.transport import RedisConsumer, RedisProducer, RedisStream, TestRunData, TestRunTask


class TestRedisConsumerAndProducer:
    """Unit tests for :class:`RedisConsumer` and :class:`RedisProducer`"""

    def test_consumer_group(self, redis_consumer: RedisConsumer) -> None:
        consumer_group = redis_consumer._consumer_group
        assert consumer_group.keys.get(RedisStream.TEST)

    def test_consume_new(
        self, redisdb, redis_consumer: RedisConsumer, redis_producer: RedisProducer, run_id: int
    ) -> None:
        task = TestRunTask(data=TestRunData(test_run_id=run_id))
        assert redis_producer.add_task(task)
        assert redis_consumer._consume()[-1].decoded_message["data"]["test_run_id"] == run_id
