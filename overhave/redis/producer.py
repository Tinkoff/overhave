import logging
from typing import Dict, Type

from overhave.entities.settings import OverhaveRedisSettings
from overhave.redis.objects import BaseRedisTask, RedisStream
from overhave.redis.template import RedisTemplate

logger = logging.getLogger(__name__)


class RedisProducer(RedisTemplate):
    """ Class for producing tasks.

    Producer send tasks into Redis stream specified by ```mapping``.
    """

    def __init__(self, settings: OverhaveRedisSettings, mapping: Dict[Type[BaseRedisTask], RedisStream]):
        super().__init__(settings)
        self._streams = {task: self._database.Stream(stream.value) for task, stream in mapping.items()}

    def add(self, task: BaseRedisTask) -> None:
        stream = self._streams[type(task)]
        logger.info("Added BaseRedisTask %s", task)
        stream.add(task.message)
