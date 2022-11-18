from overhave.transport import RedisProducer, TestRunTask, RedisConsumer, TestRunData, RedisStream


class TestRedisConsumer:
    """Unit tests for :class:`RedisConsumer`"""

    def test_consumer_group(self, redis_consumer: RedisConsumer) -> None:
        consumer_group = redis_consumer._consumer_group
        assert consumer_group.keys.get(RedisStream.TEST)

    def test_consume(self, redis_consumer: RedisConsumer, redis_producer: RedisProducer, run_id: int) -> None:
        redis_consumer._clean_pending()
        task = TestRunTask(data=TestRunData(test_run_id=run_id))
        redis_producer.add_task(task)
        assert redis_consumer._consume()[-1].decoded_message["data"]["test_run_id"] == run_id
