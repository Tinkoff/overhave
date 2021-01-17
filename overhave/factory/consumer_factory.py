from functools import cached_property
from typing import Callable, Dict, Type

from overhave.base_settings import DataBaseSettings, OverhaveLoggingSettings
from overhave.redis.consumer import RedisConsumer
from overhave.redis.objects import BaseRedisTask, EmulationTask, RedisStream, TestRunTask, TRedisTask
from overhave.redis.runner import RedisConsumerRunner


class ConsumerFactory:
    """ Factory for :class:`RedisConsumer`, :class:`RedisConsumerRunner` and tasks mapping. """

    def __init__(self, stream: RedisStream):
        self._stream = stream
        logging_settings = OverhaveLoggingSettings()
        logging_settings.setup_logging()
        DataBaseSettings().setup_db()

    @cached_property
    def _consumer(self) -> RedisConsumer:
        from overhave.entities import OverhaveRedisSettings

        return RedisConsumer(settings=OverhaveRedisSettings(), stream_name=self._stream)

    @cached_property
    def _mapping(self) -> Dict[Type[BaseRedisTask], Callable[[TRedisTask], None]]:
        from overhave.factory import proxy_factory

        return {EmulationTask: proxy_factory.emulator.start_emulation, TestRunTask: lambda _: None}  # type: ignore

    @cached_property
    def runner(self) -> RedisConsumerRunner:
        return RedisConsumerRunner(consumer=self._consumer, mapping=self._mapping)
