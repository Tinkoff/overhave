from pydantic.class_validators import validator
from pydantic.datetime_parse import timedelta
from yarl import URL

from overhave.base_settings import BaseOverhavePrefix


class BaseRedisSettings(BaseOverhavePrefix):
    """Base settings for Redis entities, which use for work with different framework tasks."""

    redis_db: int = 0
    redis_block_timeout: timedelta = timedelta(seconds=1)
    redis_read_count: int = 1
    socket_timeout: timedelta = timedelta(seconds=5)

    @property
    def timeout_milliseconds(self) -> int:
        return int(self.redis_block_timeout.total_seconds() * 1000)


class OverhaveRedisSettings(BaseRedisSettings):
    """Settings for Redis entities, which use for work with different framework tasks."""

    redis_url: URL = URL("redis://localhost:6379")

    @validator("redis_url", pre=True)
    def validate_url(cls, v: str | URL) -> URL:
        if isinstance(v, str):
            return URL(v)
        return v


class OverhaveRedisSentinelSettings(BaseRedisSettings):
    """Settings for Redis sentinel entities, which use for work with different framework tasks."""

    enabled: bool = False
    urls: list[URL] = [URL("redis://localhost:26379")]
    master_set: str
    redis_password: str

    @validator("urls", pre=True)
    def validate_urls(cls, v: list[str] | list[URL]) -> list[URL]:
        urls = []
        for url in v:
            if isinstance(url, str):
                urls.append(URL(url))
        return urls
