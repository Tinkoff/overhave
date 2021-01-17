import logging
import socket
from logging.config import DictConfigurator  # type: ignore
from typing import Any, Dict, Optional

from pydantic import BaseSettings, validator
from sqlalchemy import engine_from_config
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.pool import SingletonThreadPool


class BaseOverhavePrefix(BaseSettings):
    """ Possibility to change Overhave default settings from environment. """

    class Config:
        env_prefix = "OVERHAVE_"


class DataBaseSettings(BaseOverhavePrefix):
    """ Overhave database settings. """

    db_url: URL = 'postgresql://postgres:postgres@localhost/overhave'
    db_pool_recycle: int = 500
    db_pool_size: int = 6
    db_echo: bool = False
    db_application_name: str = socket.gethostname()
    db_connect_timeout: int = 30

    @validator('db_url', pre=True, always=True)
    def validate_url(cls, v: str) -> URL:
        try:
            return make_url(v)
        except ArgumentError as e:
            raise ValueError from e

    def create_engine(self) -> Engine:
        return engine_from_config(
            {
                'url': self.db_url,
                "pool_recycle": self.db_pool_recycle,
                "pool_pre_ping": True,
                "pool_size": self.db_pool_size,
                "poolclass": SingletonThreadPool,
                "connect_args": {
                    'connect_timeout': self.db_connect_timeout,
                    'application_name': self.db_application_name,
                },
            },
            prefix="",
        )

    def setup_db(self) -> None:
        from overhave.db.base import metadata

        metadata.bind = self.create_engine()


class OverhaveLoggingSettings(BaseOverhavePrefix):
    """ Overhave logging settings. """

    log_level: str = logging.getLevelName(logging.INFO)
    log_config: Dict[str, Any] = {}

    @validator('log_config', each_item=True)
    def dict_config_validator(cls, v: Dict[str, Any]) -> Optional[DictConfigurator]:
        if not v:
            return None
        return DictConfigurator(v)

    def setup_logging(self) -> None:
        if isinstance(self.log_config, DictConfigurator):
            self.log_config.configure()
        else:
            logging.basicConfig(level=self.log_level)
