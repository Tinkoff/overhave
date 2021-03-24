from os import chdir
from typing import Any, Callable, Dict, List, Optional, cast
from unittest import mock

import click
import pytest
import werkzeug
from _pytest.fixtures import FixtureRequest
from flask import Flask
from pytest_mock import MockFixture

from demo.demo import _run_demo_admin
from overhave import db, set_config_to_context
from overhave.admin.views import FeatureView
from overhave.admin.views.feature import _SCENARIO_PREFIX
from overhave.base_settings import DataBaseSettings
from overhave.entities import ScenarioModel, SystemUserModel
from overhave.factory import IAdminFactory, ITestExecutionFactory
from overhave.pytest_plugin import IProxyManager
from tests.objects import PROJECT_WORKDIR, FeatureTestContainer


@pytest.fixture(scope="module")
def envs_for_mock(db_settings: DataBaseSettings) -> Dict[str, Optional[str]]:
    return {"OVERHAVE_DB_URL": str(db_settings.db_url), "OVERHAVE_WORK_DIR": PROJECT_WORKDIR.as_posix()}


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def flask_run_mock() -> mock.MagicMock:
    with mock.patch.object(Flask, "run", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler


@pytest.fixture()
def click_ctx_mock() -> click.Context:
    return mock.create_autospec(click.Context)


@pytest.fixture()
def set_config_to_ctx(db_settings: DataBaseSettings, database: None, click_ctx_mock: click.Context) -> None:
    set_config_to_context(context=click_ctx_mock, settings=db_settings)


@pytest.fixture(scope="module")
def test_feature_types() -> List[str]:
    return ["feature_type_1", "feature_type_2", "feature_type_3"]


@pytest.fixture()
def test_admin_factory(clean_admin_factory: Callable[[], IAdminFactory]) -> IAdminFactory:
    return clean_admin_factory()


@pytest.fixture()
def test_testexecution_factory(
    clean_test_execution_factory: Callable[[], ITestExecutionFactory]
) -> ITestExecutionFactory:
    return clean_test_execution_factory()


@pytest.fixture()
def test_proxy_manager(clean_proxy_manager: Callable[[], IProxyManager]) -> IProxyManager:
    return clean_proxy_manager()


@pytest.fixture()
def test_resolved_admin_proxy_manager(
    flask_run_mock: mock.MagicMock,
    test_admin_factory: IAdminFactory,
    test_proxy_manager: IProxyManager,
    mock_envs: None,
    database: None,
) -> IProxyManager:
    chdir(PROJECT_WORKDIR)
    _run_demo_admin()
    return test_proxy_manager


@pytest.fixture()
def test_db_user(database: None) -> SystemUserModel:
    with db.create_session() as session:
        db_user = db.UserRole(login="test_user", password="test_password", role=db.Role.user)
        session.add(db_user)
        session.flush()
        return SystemUserModel.from_orm(db_user)


@pytest.fixture()
def test_db_scenario(test_feature_container: FeatureTestContainer, test_db_user: SystemUserModel) -> ScenarioModel:
    with db.create_session() as session:
        db_feature_type = session.query(db.FeatureType).filter(db.FeatureType.name == test_feature_container.type).one()
        db_feature = db.Feature(
            name=test_feature_container.name,
            author=test_db_user.login,
            type_id=db_feature_type.id,
            task=["PRJ-123"],
            last_edited_by=test_db_user.login,
        )
        session.add(db_feature)
        session.flush()
        db_scenario = db.Scenario(feature_id=db_feature.id, text=test_feature_container.scenario)
        session.add(db_scenario)
        session.flush()
        return ScenarioModel.from_orm(db_scenario)


@pytest.fixture()
def flask_flash_handler_mock() -> mock.MagicMock:
    with mock.patch("flask.flash", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler


@pytest.fixture()
def flask_urlfor_handler_mock(test_db_scenario: ScenarioModel) -> mock.MagicMock:
    with mock.patch(
        "flask.url_for", return_value=f"/testrun/details/?id={test_db_scenario.id}"
    ) as flask_urlfor_handler:
        yield flask_urlfor_handler


@pytest.fixture(scope="module")
def subprocess_run_mock() -> mock.MagicMock:
    returncode_mock = mock.MagicMock()
    returncode_mock.returncode = 0
    with mock.patch("subprocess.run", return_value=returncode_mock) as mocked_subprocess_run:
        yield mocked_subprocess_run


@pytest.fixture(scope="module")
def test_rendered_featureview(module_mocker: MockFixture) -> mock.MagicMock:
    return module_mocker.create_autospec(werkzeug.Response)


@pytest.fixture()
def redisproducer_addtask_mock(test_resolved_admin_proxy_manager: IProxyManager) -> mock.MagicMock:
    with mock.patch.object(
        test_resolved_admin_proxy_manager.factory.redis_producer, "add_task", return_value=mock.MagicMock()
    ) as mocked_redisproducer_addtask:
        yield mocked_redisproducer_addtask


@pytest.fixture()
def flask_currentuser_mock(test_db_user: SystemUserModel) -> mock.MagicMock:
    with mock.patch("overhave.admin.views.feature.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = test_db_user.login
        yield mocked


@pytest.fixture()
def runtest_data(test_db_scenario: ScenarioModel, request: FixtureRequest) -> Dict[str, Any]:
    if hasattr(request, "param"):
        return cast(Dict[str, Any], request.param)
    # regular data
    return {
        f"{_SCENARIO_PREFIX}-id": test_db_scenario.id,
        f"{_SCENARIO_PREFIX}-text": test_db_scenario.text,
    }


@pytest.fixture()
def test_featureview_runtest_result(
    test_rendered_featureview: mock.MagicMock,
    test_resolved_admin_proxy_manager: IProxyManager,
    test_db_scenario: ScenarioModel,
    flask_flash_handler_mock: mock.MagicMock,
    flask_urlfor_handler_mock: mock.MagicMock,
    redisproducer_addtask_mock: mock.MagicMock,
    flask_currentuser_mock: mock.MagicMock,
    runtest_data: Dict[str, Any],
) -> werkzeug.Response:
    return FeatureView._run_test(data=runtest_data, rendered=test_rendered_featureview)
