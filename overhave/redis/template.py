import walrus

from overhave.entities.settings import OverhaveRedisSettings


class RedisTemplate:
    """ Base class for :class:`RedisProducer` and :class:`RedisConsumer`. """

    def __init__(self, settings: OverhaveRedisSettings):
        self._settings = settings
        self._database = walrus.Database(
            host=settings.redis_url.host, port=settings.redis_url.port, db=settings.redis_db, retry_on_timeout=True
        )
