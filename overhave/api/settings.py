from pydantic.env_settings import BaseSettings

from overhave.base_settings import OVERHAVE_ENV_PREFIX


class OverhaveApiSettings(BaseSettings):
    """Settings for Overhave API server, started with Uvicorn."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    class Config:
        env_prefix = OVERHAVE_ENV_PREFIX + "UVICORN_"
