from datetime import timedelta
from typing import Optional, Tuple, TypeVar

from pydantic import BaseSettings, validator
from yarl import URL

from overhave.utils import make_url


class BaseHttpClientSettings(BaseSettings):
    """Base settings for :class:`BaseHttpClient`."""

    url: URL

    connect_timeout: timedelta = timedelta(seconds=1)
    read_timeout: timedelta = timedelta(seconds=5)

    @validator("url", pre=True)
    def make_url(cls, v: Optional[str]) -> Optional[URL]:
        return make_url(v)

    @property
    def timeout(self) -> Tuple[float, float]:
        return self.connect_timeout.total_seconds(), self.read_timeout.total_seconds()


HttpSettingsType = TypeVar("HttpSettingsType", bound=BaseHttpClientSettings)
