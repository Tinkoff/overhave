import httpx

from overhave.base_settings import OVERHAVE_ENV_PREFIX
from overhave.transport.http.base_client import BaseHttpClientSettings


class OverhaveApiAuthenticatorSettings(BaseHttpClientSettings):
    """Settings for :class:`OverhaveApiAuthenticator`."""

    auth_token_path: str = "token"

    class Config:
        env_prefix = OVERHAVE_ENV_PREFIX + "API_AUTH_"

    @property
    def get_auth_token_url(self) -> httpx.URL:
        return httpx.URL(f"{self.url}/{self.auth_token_path}")
