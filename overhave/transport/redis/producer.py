import logging

import redis
import walrus

from overhave.metrics import BaseOverhaveMetricContainer
from overhave.transport.redis.objects import BaseRedisTask, RedisStream
from overhave.transport.redis.settings import BaseRedisSettings

logger = logging.getLogger(__name__)


class RedisProducer:
    """Class for producing tasks.

    Producer send tasks into Redis stream specified by ```mapping``.
    """

    def __init__(
        self,
        settings: BaseRedisSettings,
        mapping: dict[type[BaseRedisTask], RedisStream],
        database: walrus.Database,
        metric_container: BaseOverhaveMetricContainer,
    ):
        self._settings = settings
        self._streams = {task: database.Stream(stream.value) for task, stream in mapping.items()}
        self._mapping = mapping
        self._metric_container = metric_container

    def add_task(self, task: BaseRedisTask) -> bool:
        stream = self._streams[type(task)]
        logger.info("Added Redis task %s", task)
        try:
            stream.add(task.message)
            self._metric_container.produce_redis_task(task_type=self._mapping[type(task)].value)
            return True
        except redis.exceptions.ConnectionError:
            logger.exception("Could not add %s to Redis!", type(task).__name__)
            return False
