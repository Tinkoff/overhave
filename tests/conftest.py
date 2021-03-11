import logging
from pathlib import Path
from typing import Callable, Dict, Iterator, Optional, cast, Any
import os
import tempfile
import py
import pytest
import sqlalchemy_utils as sau
from pytest_mock import MockFixture
from sqlalchemy import MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import close_all_sessions

from overhave import AuthorizationStrategy, OverhaveContext, OverhaveAppType, overhave_app
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


@pytest.fixture(scope="session")
def db_context(db_settings: DataBaseSettings) -> Iterator[DataBaseContext]:
    from overhave.db import metadata

    if sau.database_exists(db_settings.db_url):
        sau.drop_database(db_settings.db_url)
    sau.create_database(db_settings.db_url)
    engine = create_engine(db_settings.db_url, echo=db_settings.db_echo, pool_pre_ping=True)
    db_context = DataBaseContext(metadata=metadata, engine=engine)
    db_context.metadata.bind = db_context.engine
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
    db_context.metadata.drop_all()
    db_context.metadata.create_all()
    yield
    close_all_sessions()


@pytest.fixture(scope="module")
def mock_envs(envs_for_mock: Dict[str, Optional[str]], mock_default_value: str) -> Iterator[None]:
    old_values = {key: os.environ.get(key) for key in envs_for_mock}
    try:
        for key in envs_for_mock:
            os.environ[key] = envs_for_mock.get(key) or mock_default_value
        yield
    finally:
        for key, value in old_values.items():
            os.environ[key] = value or ""


@pytest.fixture()
def clean_proxy_factory() -> Callable[[], ProxyFactory]:
    get_proxy_factory.cache_clear()
    return get_proxy_factory


@pytest.fixture()
def mocked_context(session_mocker: MockFixture, tmpdir: py.path.local) -> OverhaveContext:
    context_mock = session_mocker.MagicMock()
    context_mock.auth_settings.auth_strategy = AuthorizationStrategy.LDAP
    context_mock.s3_manager_settings.enabled = False

    root_tmp_dir = Path(tmpdir)
    features_dir = root_tmp_dir / "features"
    fixtures_dir = root_tmp_dir / "fixtures"
    reports_dir = root_tmp_dir / "reports"
    for path in (features_dir, fixtures_dir, reports_dir):
        path.mkdir()
    context_mock.file_settings.tmp_features_dir = features_dir
    context_mock.file_settings.tmp_fixtures_dir = fixtures_dir
    context_mock.file_settings.tmp_reports_dir = reports_dir

    return cast(OverhaveContext, context_mock)


@pytest.fixture()
def patched_app_proxy_factory(
    db_settings: DataBaseSettings,
    database: None,
    mocked_context: OverhaveContext,
    clean_proxy_factory: Callable[[], ProxyFactory],
) -> ProxyFactory:
    db_settings.setup_db()
    factory = clean_proxy_factory()
    factory.set_context(mocked_context)
    return factory


@pytest.fixture()
def test_app(patched_app_proxy_factory: ProxyFactory) -> OverhaveAppType:
    return overhave_app(factory=patched_app_proxy_factory)


@pytest.fixture()
def test_client(test_app: OverhaveAppType) -> Any:
    db_fd, test_app.config["DATABASE"] = tempfile.mkstemp()
    test_app.config["TESTING"] = True

    with test_app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(test_app.config["DATABASE"])
