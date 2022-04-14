from datetime import timedelta

from pydantic.env_settings import BaseSettings
from pydantic.types import SecretStr

from overhave.base_settings import OVERHAVE_ENV_PREFIX


class OverhaveUvicornApiSettings(BaseSettings):
    """Settings for Overhave API server, started with Uvicorn."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    class Config:
        env_prefix = OVERHAVE_ENV_PREFIX + "UVICORN_"


class OverhaveApiAuthSettings(BaseSettings):
    """Settings for Overhave API service auth_managers."""

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def access_token_expire_timedelta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    class Config:
        env_prefix = OVERHAVE_ENV_PREFIX + "API_AUTH_"
