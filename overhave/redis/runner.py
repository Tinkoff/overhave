import logging
from typing import Callable, Dict, Type

from overhave.redis.consumer import RedisConsumer
from overhave.redis.objects import BaseRedisTask, RedisContainer, RedisUnreadData, TRedisTask

logger = logging.getLogger(__name__)


class RedisConsumerRunnerException(Exception):
    """ Exception for RedisConsumerRunner errors. """

    pass


class RedisConsumerRunner:
    """ Class for running tasks specified by ```mapping```.

    Runner tasks launch with instance of :class:`RedisConsumer` ```consumer```.
    """

    def __init__(
        self, consumer: RedisConsumer, mapping: Dict[Type[BaseRedisTask], Callable[[TRedisTask], None]]
    ) -> None:
        self._consumer = consumer
        self._mapping = mapping  # type: ignore

    def run(self) -> None:
        try:
            self._run()
        except Exception as e:
            raise RedisConsumerRunnerException from e

        logger.info("Shutdown event reached")

    def _run(self) -> None:
        with self._consumer:
            for message_sequence in self._consumer:
                for msg in message_sequence:
                    self._process(msg)

    def _process(self, data: RedisUnreadData) -> None:
        container = RedisContainer(task=data.decoded_message)
        logger.info("Gotten ready for processing BaseRedisTask: %s", container.task)
        self._mapping[type(container.task)](container.task)
