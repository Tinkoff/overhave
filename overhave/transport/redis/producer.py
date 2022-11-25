import logging
from typing import Dict, Type

import redis

from overhave.transport.redis.objects import BaseRedisTask, RedisStream
from overhave.transport.redis.settings import OverhaveRedisSentinelSettings, OverhaveRedisSettings
from overhave.transport.redis.template import RedisTemplate

logger = logging.getLogger(__name__)


class RedisProducer(RedisTemplate):
    """Class for producing tasks.

    Producer send tasks into Redis stream specified by ```mapping``.
    """

    def __init__(
        self,
        settings: OverhaveRedisSettings,
        sentinel_settings: OverhaveRedisSentinelSettings,
        mapping: Dict[Type[BaseRedisTask], RedisStream],
    ):
        super().__init__(settings, sentinel_settings)
        self._streams = {task: self._database.Stream(stream.value) for task, stream in mapping.items()}

    def add_task(self, task: BaseRedisTask) -> bool:
        stream = self._streams[type(task)]
        logger.info("Added Redis task %s", task)
        try:
            stream.add(task.message)
            return True
        except redis.exceptions.ConnectionError:
            logger.exception("Could not add %s to Redis!", type(task).__name__)
            return False
