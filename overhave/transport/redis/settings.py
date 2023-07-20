from datetime import timedelta

import yarl
from pydantic import field_validator
from pydantic_settings import BaseSettings


class BaseRedisSettings(BaseSettings):
    """Base settings for Redis entities, which use for work with different framework tasks."""

    db: int = 0
    block_timeout: timedelta = timedelta(seconds=1)
    read_count: int = 1
    socket_timeout: timedelta = timedelta(seconds=5)

    @property
    def timeout_milliseconds(self) -> int:
        return int(self.block_timeout.total_seconds() * 1000)

    class Config:
        env_prefix = "OVERHAVE_REDIS_"


class OverhaveRedisSettings(BaseRedisSettings):
    """Settings for Redis entities, which use for work with different framework tasks."""

    url: yarl.URL = yarl.URL("redis://localhost:6379")

    @field_validator("url", mode="before")
    def validate_url(cls, v: str | yarl.URL) -> yarl.URL:
        if isinstance(v, str):
            return yarl.URL(v)
        return v


class OverhaveRedisSentinelSettings(BaseRedisSettings):
    """Settings for Redis sentinel entities, which use for work with different framework tasks."""

    enabled: bool = False
    urls: list[yarl.URL] = [yarl.URL("redis://localhost:6379")]
    master_set: str = "foo"
    password: str = "bar"

    @field_validator("urls", mode="before")
    def validate_urls(cls, v: list[str] | list[yarl.URL]) -> list[yarl.URL]:
        urls = []
        for url in v:
            if isinstance(url, str):
                urls.append(yarl.URL(url))
            if isinstance(url, yarl.URL):
                urls.append(url)
        return urls

    class Config:
        env_prefix = "OVERHAVE_REDIS_SENTINEL_"
