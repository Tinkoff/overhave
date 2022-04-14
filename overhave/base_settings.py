import enum
import logging
import socket
from logging.config import DictConfigurator  # type: ignore
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field, validator
from sqlalchemy import engine_from_config
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.pool import SingletonThreadPool

OVERHAVE_ENV_PREFIX = "OVERHAVE_"


class BaseOverhavePrefix(BaseSettings):
    """Possibility to change Overhave default settings from environment."""

    class Config:
        env_prefix = OVERHAVE_ENV_PREFIX


class SAUrl(URL):
    """Custom SQLAlchemy URL for Pydantic BaseSettings validation."""

    @classmethod
    def __get_validators__(cls):  # type: ignore
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> URL:
        try:
            return make_url(v)
        except ArgumentError as e:
            raise ValueError from e


class DataBaseSettings(BaseOverhavePrefix):
    """Overhave database settings."""

    db_url: SAUrl = Field(SAUrl.validate("postgresql://postgres:postgres@localhost/overhave"))
    db_pool_recycle: int = 500
    db_pool_size: int = 6
    db_echo: bool = False
    db_application_name: str = socket.gethostname()
    db_connect_timeout: int = 30

    def create_engine(self) -> Engine:
        return engine_from_config(
            {
                "url": self.db_url,
                "pool_recycle": self.db_pool_recycle,
                "pool_pre_ping": True,
                "pool_size": self.db_pool_size,
                "poolclass": SingletonThreadPool,
                "connect_args": {
                    "connect_timeout": self.db_connect_timeout,
                    "application_name": self.db_application_name,
                },
            },
            prefix="",
        )

    def setup_db(self) -> None:
        from overhave.db.base import metadata

        metadata.bind = self.create_engine()


class LoggingSettings(BaseOverhavePrefix):
    """Overhave logging settings."""

    log_level: str = logging.getLevelName(logging.INFO)
    log_config: Dict[str, Any] = {}

    @validator("log_config", each_item=True)
    def dict_config_validator(cls, v: Dict[str, Any]) -> Optional[DictConfigurator]:
        if not v:
            return None
        return DictConfigurator(v)

    def setup_logging(self) -> None:
        if isinstance(self.log_config, DictConfigurator):
            self.log_config.configure()
        else:
            logging.basicConfig(level=self.log_level)


class AuthorizationStrategy(str, enum.Enum):
    """
    Authorization strategies Enum.

    Simple - strategy without real auth_managers. Each user could use preferred name. This name will be used for user
    authority. Each user is unique. Password not required.
    Default - strategy with real auth_managers. Each user could use only registered credentials.
    LDAP - strategy with auth_managers using remote LDAP server. Each user should use his LDAP credentials. LDAP
    server returns user groups. If user in default 'admin' group or his groups list contains admin group - user
    will be authorized. If user already placed in database - user will be authorized too. No one password stores.
    """

    SIMPLE = "simple"
    DEFAULT = "default"
    LDAP = "ldap"


class OverhaveAuthorizationSettings(BaseOverhavePrefix):
    """Settings for Overhave auth_managers in components interface.

    Supports 3 strategies: SIMPLE, DEFAULT and LDAP.
    LDAP auth_managers uses group politics with administration group `admin_group`.
    SIMPLE and DEFAULT strategies use admin user that would be dynamically created at startup.
    """

    auth_strategy: AuthorizationStrategy = AuthorizationStrategy.SIMPLE
