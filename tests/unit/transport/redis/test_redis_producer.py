from overhave.transport import RedisProducer, TestRunTask, TestRunData, RedisConsumer


class TestRedisProducer:
    """Unit tests for :class:`RedisProducer`"""
    def test_add_task(self, redis_producer: RedisProducer, run_id: int) -> None:
        task = TestRunTask(data=TestRunData(test_run_id=run_id))
        assert redis_producer.add_task(task)
