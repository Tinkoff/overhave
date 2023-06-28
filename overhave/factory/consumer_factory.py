from functools import cached_property, partial
from typing import Callable

import walrus

from overhave.factory.getters import get_emulation_factory, get_publication_factory, get_test_execution_factory
from overhave.metrics import get_common_metric_container
from overhave.pytest_plugin import get_proxy_manager
from overhave.transport import (
    AnyRedisTask,
    EmulationTask,
    PublicationTask,
    RedisConsumer,
    RedisConsumerRunner,
    RedisStream,
    TestRunTask,
)
from overhave.transport.redis.deps import get_redis_settings, make_redis


class ConsumerFactory:
    """Factory for :class:`RedisConsumer`, :class:`RedisConsumerRunner` and tasks mapping."""

    def __init__(self, stream: RedisStream):
        self._stream = stream

    @cached_property
    def _database(self) -> walrus.Database:
        redis = make_redis(get_redis_settings())
        return walrus.Database(connection_pool=redis.connection_pool)

    @cached_property
    def _consumer(self) -> RedisConsumer:
        return RedisConsumer(
            settings=get_redis_settings(),
            stream_name=self._stream,
            database=self._database,
            metric_container=get_common_metric_container(),
        )

    @cached_property
    def runner(self) -> RedisConsumerRunner:
        return RedisConsumerRunner(consumer=self._consumer, mapping=self._mapping)

    @cached_property
    def _mapping(self) -> dict[type[AnyRedisTask], Callable[[AnyRedisTask], None]]:
        return {
            TestRunTask: self._process_test_execution_task,  # type: ignore
            PublicationTask: get_publication_factory().process_task,  # type: ignore
            EmulationTask: get_emulation_factory().process_task,  # type: ignore
        }

    @cached_property
    def _process_test_execution_task(self) -> Callable[[TestRunTask], None]:
        factory = get_test_execution_factory()
        proxy_manager = get_proxy_manager()
        proxy_manager.set_factory(factory)
        return partial(
            factory.process_task,
        )
