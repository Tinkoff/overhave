from datetime import timedelta
from typing import TypeVar

import httpx
from pydantic import BaseSettings, validator

from overhave.utils import make_url


class BaseHttpClientSettings(BaseSettings):
    """Base settings for :class:`BaseHttpClient`."""

    url: httpx.URL

    default_timeout: timedelta | None = None
    connect_timeout: timedelta = timedelta(seconds=1)
    read_timeout: timedelta = timedelta(seconds=5)
    write_timeout: timedelta | None = None
    pool_timeout: timedelta | None = None

    @validator("url", pre=True)
    def make_url(cls, v: str | None) -> httpx.URL | None:
        return make_url(v)

    @staticmethod
    def _as_optional_timeout(timeout: timedelta | None) -> float | None:
        if timeout is not None:
            return timeout.total_seconds()
        return None

    @property
    def timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            self._as_optional_timeout(self.default_timeout),
            connect=self.connect_timeout.total_seconds(),
            read=self.read_timeout.total_seconds(),
            write=self._as_optional_timeout(self.write_timeout),
            pool=self._as_optional_timeout(self.pool_timeout),
        )


HttpSettingsType = TypeVar("HttpSettingsType", bound=BaseHttpClientSettings)
