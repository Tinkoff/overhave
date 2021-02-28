import logging
from typing import Callable, Iterator, cast

import pytest
import sqlalchemy_utils as sau
from pytest_mock import MockFixture
from sqlalchemy import MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import close_all_sessions

from overhave import AuthorizationStrategy, OverhaveContext
from overhave.base_settings import DataBaseSettings, OverhaveLoggingSettings
from overhave.factory import ProxyFactory, get_proxy_factory
from tests.objects import DataBaseContext, XDistWorkerValueType


@pytest.fixture(scope="session", autouse=True)
def setup_logging() -> None:
    OverhaveLoggingSettings(log_level=logging.DEBUG).setup_logging()


@pytest.fixture(scope="session")
def db_settings(worker_id: XDistWorkerValueType) -> DataBaseSettings:
    settings = DataBaseSettings()
    settings.db_url = f"{settings.db_url}/overhave_{worker_id}"
    return settings


def create_metadata(db_context: DataBaseContext) -> None:
    db_context.metadata.bind = db_context.engine
    db_context.metadata.drop_all()
    db_context.metadata.create_all()


@pytest.fixture(scope="session")
def db_context(db_settings: DataBaseSettings) -> Iterator[DataBaseContext]:
    from overhave.db import metadata

    if sau.database_exists(db_settings.db_url):
        sau.drop_database(db_settings.db_url)
    sau.create_database(db_settings.db_url)
    engine = create_engine(db_settings.db_url, echo=db_settings.db_echo, pool_pre_ping=True)
    db_context = DataBaseContext(metadata=metadata, engine=engine)
    create_metadata(db_context)
    yield db_context
    sau.drop_database(db_settings.db_url)


def truncate_all_tables(metadata: MetaData) -> None:
    connection = metadata.bind.connect()
    transaction = connection.begin()

    for table in metadata.sorted_tables:
        connection.execute(table.delete())

    transaction.commit()
    connection.close()


@pytest.fixture()
def database(db_context: DataBaseContext) -> Iterator[None]:
    truncate_all_tables(db_context.metadata)
    yield
    close_all_sessions()


@pytest.fixture()
def clean_proxy_factory() -> Callable[[], ProxyFactory]:
    get_proxy_factory.cache_clear()
    return get_proxy_factory


@pytest.fixture(scope="class")
def mocked_context(session_mocker: MockFixture) -> OverhaveContext:
    context_mock = session_mocker.MagicMock()
    context_mock.auth_settings.auth_strategy = AuthorizationStrategy.LDAP
    context_mock.s3_manager_settings.enabled = False
    return cast(OverhaveContext, context_mock)
