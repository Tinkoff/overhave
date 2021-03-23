import logging
import os
from pathlib import Path
from typing import Callable, Dict, Iterator, Optional, Sequence, cast

import py
import pytest
import sqlalchemy_utils as sau
from _pytest.python import Metafunc
from pytest_mock import MockFixture
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import close_all_sessions

from overhave import (
    AuthorizationStrategy,
    LoggingSettings,
    OverhaveAdminContext,
    OverhaveDBSettings,
    overhave_admin_factory,
    overhave_emulation_factory,
    overhave_publication_factory,
    overhave_test_execution_factory,
)
from overhave.factory import IAdminFactory, ITestExecutionFactory
from overhave.factory.components import IEmulationFactory, IPublicationFactory
from tests.objects import DataBaseContext, FeatureTestContainer, XDistWorkerValueType, get_test_feature_containers


@pytest.fixture(scope="session", autouse=True)
def setup_logging() -> None:
    LoggingSettings(log_level=logging.DEBUG).setup_logging()


@pytest.fixture(scope="session")
def db_settings(worker_id: XDistWorkerValueType) -> OverhaveDBSettings:
    settings = OverhaveDBSettings()
    settings.db_url = f"{settings.db_url}/overhave_{worker_id}"
    return settings


@pytest.fixture(scope="session")
def db_context(db_settings: OverhaveDBSettings) -> Iterator[DataBaseContext]:
    from overhave.db import metadata

    if sau.database_exists(db_settings.db_url):
        sau.drop_database(db_settings.db_url)
    sau.create_database(db_settings.db_url)
    engine = create_engine(db_settings.db_url, echo=db_settings.db_echo, pool_pre_ping=True)
    db_context = DataBaseContext(metadata=metadata, engine=engine)
    db_context.metadata.bind = db_context.engine
    yield db_context
    sau.drop_database(db_settings.db_url)


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
def clean_admin_factory() -> Callable[[], IAdminFactory]:
    overhave_admin_factory.cache_clear()
    return overhave_admin_factory


@pytest.fixture()
def clean_test_execution_factory() -> Callable[[], ITestExecutionFactory]:
    overhave_test_execution_factory.cache_clear()
    return overhave_test_execution_factory


@pytest.fixture()
def clean_publication_factory() -> Callable[[], IPublicationFactory]:
    overhave_publication_factory.cache_clear()
    return overhave_publication_factory


@pytest.fixture()
def clean_emulation_factory() -> Callable[[], IEmulationFactory]:
    overhave_emulation_factory.cache_clear()
    return overhave_emulation_factory


@pytest.fixture()
def mocked_context(session_mocker: MockFixture, tmpdir: py.path.local) -> OverhaveAdminContext:
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

    return cast(OverhaveAdminContext, context_mock)


@pytest.fixture(scope="session")
def test_feature_containers() -> Sequence[FeatureTestContainer]:
    return cast(Sequence[FeatureTestContainer], get_test_feature_containers())


def pytest_generate_tests(metafunc: Metafunc) -> None:
    test_feature_container_name = "test_feature_container"
    if test_feature_container_name in metafunc.fixturenames:
        metafunc.parametrize(test_feature_container_name, get_test_feature_containers())
