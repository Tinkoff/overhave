from functools import cached_property, partial
from typing import Callable, Dict, Type

from overhave.factory.getters import get_emulation_factory, get_publication_factory, get_test_execution_factory
from overhave.pytest_plugin import get_proxy_manager
from overhave.transport.redis.consumer import RedisConsumer
from overhave.transport.redis.objects import (
    BaseRedisTask,
    EmulationTask,
    PublicationTask,
    RedisStream,
    TestRunTask,
    TRedisTask,
)
from overhave.transport.redis.runner import RedisConsumerRunner


class ConsumerFactory:
    """ Factory for :class:`RedisConsumer`, :class:`RedisConsumerRunner` and tasks mapping. """

    def __init__(self, stream: RedisStream):
        self._stream = stream

    @cached_property
    def _consumer(self) -> RedisConsumer:
        from overhave.entities import OverhaveRedisSettings

        return RedisConsumer(settings=OverhaveRedisSettings(), stream_name=self._stream)

    @cached_property
    def runner(self) -> RedisConsumerRunner:
        return RedisConsumerRunner(consumer=self._consumer, mapping=self._mapping)

    @cached_property
    def _mapping(self) -> Dict[Type[BaseRedisTask], Callable[[TRedisTask], None]]:
        return {
            TestRunTask: self._process_test_execution,
            PublicationTask: self._process_publication,
            EmulationTask: self._process_emulation,
        }

    @cached_property
    def _process_test_execution(self) -> Callable[[TestRunTask], None]:
        factory = get_test_execution_factory()
        proxy_manager = get_proxy_manager()
        proxy_manager.set_factory(factory)
        return partial(factory.test_execution_manager.execute_test)

    @cached_property
    def _process_publication(self) -> Callable[[PublicationTask], None]:
        return partial(get_publication_factory().publisher.publish_version)

    @cached_property
    def _process_emulation(self) -> Callable[[PublicationTask], None]:
        return partial(get_emulation_factory().emulator.start_emulation)
