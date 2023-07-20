import logging
import os
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence, cast
from unittest import mock

import httpx
import py
import pytest
import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy_utils as sau
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture
from _pytest.python import Metafunc
from prometheus_client import CollectorRegistry
from pytest_mock import MockerFixture
from sqlalchemy import event

from overhave import (
    OverhaveAdminSettings,
    OverhaveAuthorizationStrategy,
    OverhaveDBSettings,
    OverhaveLoggingSettings,
    OverhaveScenarioCompilerSettings,
    OverhaveScenarioParserSettings,
    db,
    overhave_admin_factory,
    overhave_proxy_manager,
    overhave_synchronizer_factory,
    overhave_test_execution_factory,
)
from overhave.factory import IAdminFactory, ISynchronizerFactory, ITestExecutionFactory
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.metrics import (
    BaseOverhaveMetricContainer,
    EmulationRunOverhaveMetricContainer,
    PublicationOverhaveMetricContainer,
    TestRunOverhaveMetricContainer,
)
from overhave.pytest_plugin import IProxyManager
from tests.db_utils import BEFORE_CURSOR_EXECUTE_EVENT_NAME, THREAD_LOCALS, validate_db_session
from tests.objects import PROJECT_WORKDIR, FeatureTestContainer, XDistWorkerValueType, get_test_feature_containers


@pytest.fixture(autouse=True)
def setup_logging(caplog: LogCaptureFixture, request: FixtureRequest) -> None:
    THREAD_LOCALS.fixture_request = request
    caplog.set_level(logging.DEBUG)
    OverhaveLoggingSettings().setup_logging()


@pytest.fixture(scope="session")
def db_settings(worker_id: XDistWorkerValueType) -> OverhaveDBSettings:
    settings = OverhaveDBSettings(db_echo=True)
    settings.db_url = sa.make_url(f"{settings.db_url.render_as_string(hide_password=False)}/overhave_{worker_id}")
    return settings


@pytest.fixture(scope="session")
def db_metadata(db_settings: OverhaveDBSettings) -> Iterator[db.SAMetadata]:
    from overhave.db import metadata

    engine = sa.create_engine(db_settings.db_url, echo=db_settings.db_echo, pool_pre_ping=True)

    if sau.database_exists(engine.url):
        sau.drop_database(engine.url)
    sau.create_database(engine.url)

    metadata.set_engine(engine)
    yield metadata
    sau.drop_database(engine.url)


@pytest.fixture(scope="module")
def use_sql_counter() -> Iterator[None]:
    THREAD_LOCALS.need_sql_counter = True
    yield
    THREAD_LOCALS.need_sql_counter = False


@pytest.fixture()
def database(use_sql_counter: None, db_metadata: db.SAMetadata) -> Iterator[None]:
    db_metadata.drop_all(bind=db_metadata.engine)
    db_metadata.create_all(bind=db_metadata.engine)

    with ExitStack():
        event.listen(sa.Engine, BEFORE_CURSOR_EXECUTE_EVENT_NAME, validate_db_session)
        yield
        event.remove(sa.Engine, BEFORE_CURSOR_EXECUTE_EVENT_NAME, validate_db_session)
    so.close_all_sessions()


@pytest.fixture(scope="module")
def mock_envs(envs_for_mock: dict[str, str | None], mock_default_value: str) -> Iterator[None]:
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
    yield overhave_admin_factory
    overhave_admin_factory.cache_clear()


@pytest.fixture()
def clean_test_execution_factory() -> Callable[[], ITestExecutionFactory]:
    overhave_test_execution_factory.cache_clear()
    yield overhave_test_execution_factory
    overhave_test_execution_factory.cache_clear()


@pytest.fixture()
def clean_proxy_manager() -> Callable[[], IProxyManager]:
    overhave_proxy_manager.cache_clear()
    yield overhave_proxy_manager
    overhave_proxy_manager.cache_clear()


@pytest.fixture()
def clean_synchronizer_factory() -> Callable[[], ISynchronizerFactory]:
    overhave_synchronizer_factory.cache_clear()
    yield overhave_synchronizer_factory
    overhave_synchronizer_factory.cache_clear()


@pytest.fixture()
def mocked_context(session_mocker: MockerFixture, tmpdir: py.path.local) -> BaseFactoryContext:
    context_mock = session_mocker.MagicMock()
    context_mock.auth_settings.auth_strategy = OverhaveAuthorizationStrategy.LDAP
    context_mock.s3_manager_settings.enabled = False
    context_mock.compilation_settings = OverhaveScenarioCompilerSettings()
    context_mock.parser_settings = OverhaveScenarioParserSettings()

    if os.environ.get("TEST_SUPPORT_CHAT_URL"):
        test_support_chat_url = httpx.URL(os.environ["TEST_SUPPORT_CHAT_URL"])
    else:
        test_support_chat_url = None
    context_mock.admin_settings = OverhaveAdminSettings(support_chat_url=test_support_chat_url)

    root_dir = Path(tmpdir)
    features_dir = root_dir / "features"
    fixtures_dir = root_dir / "fixtures"
    reports_dir = root_dir / "reports"
    for path in (features_dir, fixtures_dir, reports_dir):
        path.mkdir()
    context_mock.file_settings.tmp_features_dir = features_dir
    context_mock.file_settings.tmp_fixtures_dir = fixtures_dir
    context_mock.file_settings.tmp_reports_dir = reports_dir

    return cast("BaseFactoryContext", context_mock)


@pytest.fixture(scope="session")
def step_prefixes_backup() -> list[tuple[Any, ...]]:
    from pytest_bdd.parser import STEP_PREFIXES

    return deepcopy(STEP_PREFIXES)


@pytest.fixture(autouse=True)
def step_prefixes_clean(step_prefixes_backup: list[tuple[Any, ...]]) -> None:
    from pytest_bdd.parser import STEP_PREFIXES

    STEP_PREFIXES.clear()
    STEP_PREFIXES.extend(step_prefixes_backup)


@pytest.fixture(scope="session")
def test_feature_containers() -> Sequence[FeatureTestContainer]:
    return cast(Sequence[FeatureTestContainer], get_test_feature_containers())


def pytest_generate_tests(metafunc: Metafunc) -> None:
    test_feature_container_name = "test_feature_container"
    if test_feature_container_name in metafunc.fixturenames:
        metafunc.parametrize(test_feature_container_name, get_test_feature_containers())


@pytest.fixture(scope="session", autouse=True)
def flask_scaffold_findpackagepath_mock() -> Iterator[None]:
    with mock.patch("flask.scaffold._find_package_path", return_value=PROJECT_WORKDIR.as_posix()):
        yield


@pytest.fixture()
def registry() -> CollectorRegistry:
    return CollectorRegistry()


@pytest.fixture()
def base_container(registry: CollectorRegistry) -> BaseOverhaveMetricContainer:
    return BaseOverhaveMetricContainer(registry=registry)


@pytest.fixture()
def test_container(registry: CollectorRegistry) -> TestRunOverhaveMetricContainer:
    return TestRunOverhaveMetricContainer(registry=registry)


@pytest.fixture()
def emulation_container(registry: CollectorRegistry) -> EmulationRunOverhaveMetricContainer:
    return EmulationRunOverhaveMetricContainer(registry=registry)


@pytest.fixture()
def publication_container(registry: CollectorRegistry) -> PublicationOverhaveMetricContainer:
    return PublicationOverhaveMetricContainer(registry=registry)
