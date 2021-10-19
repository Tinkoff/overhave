from os import chdir
from typing import Any, Callable, Dict, Optional, Tuple, cast
from unittest import mock

import pytest
import werkzeug
from _pytest.fixtures import FixtureRequest
from faker import Faker
from flask import Flask

from demo.demo import _run_demo_admin
from demo.settings import OverhaveDemoAppLanguage, OverhaveDemoSettingsGenerator
from overhave import OverhaveDBSettings, db
from overhave.admin.views.feature import _SCENARIO_PREFIX, FeatureView
from overhave.entities import ScenarioModel, SystemUserModel
from overhave.factory import IAdminFactory
from overhave.pytest_plugin import IProxyManager
from tests.objects import PROJECT_WORKDIR, FeatureTestContainer


@pytest.fixture(scope="module")
def envs_for_mock(db_settings: OverhaveDBSettings) -> Dict[str, Optional[str]]:
    return {"OVERHAVE_DB_URL": str(db_settings.db_url), "OVERHAVE_WORK_DIR": PROJECT_WORKDIR.as_posix()}


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def test_proxy_manager(clean_proxy_manager: Callable[[], IProxyManager]) -> IProxyManager:
    return clean_proxy_manager()


@pytest.fixture()
def test_system_user_login(request: FixtureRequest, faker: Faker) -> str:
    if hasattr(request, "param"):
        return cast(str, request.param)
    return faker.word()


@pytest.fixture()
def test_db_user(database: None, test_system_user_login: str) -> SystemUserModel:
    with db.create_session() as session:
        db_user = db.UserRole(login=test_system_user_login, password="test_password", role=db.Role.user)
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
            file_path=test_feature_container.file_path,
        )
        session.add(db_feature)
        session.flush()
        db_scenario = db.Scenario(feature_id=db_feature.id, text=test_feature_container.scenario)
        session.add(db_scenario)
        session.flush()
        return ScenarioModel.from_orm(db_scenario)


@pytest.fixture()
def flask_run_mock() -> mock.MagicMock:
    with mock.patch.object(Flask, "run", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler


@pytest.fixture(scope="module")
def test_feature_types() -> Tuple[str, ...]:
    return "feature_type_1", "feature_type_2", "feature_type_3"


@pytest.fixture()
def test_admin_factory(clean_admin_factory: Callable[[], IAdminFactory]) -> IAdminFactory:
    return clean_admin_factory()


@pytest.fixture()
def test_demo_language(request: FixtureRequest) -> Optional[str]:
    if hasattr(request, "param"):
        return cast(OverhaveDemoAppLanguage, request.param)
    raise NotImplementedError


@pytest.fixture()
def test_demo_settings_generator(test_demo_language: OverhaveDemoAppLanguage) -> OverhaveDemoSettingsGenerator:
    return OverhaveDemoSettingsGenerator(language=test_demo_language, threadpool=False)


@pytest.fixture()
def test_resolved_admin_proxy_manager(
    flask_run_mock: mock.MagicMock,
    test_admin_factory: IAdminFactory,
    test_proxy_manager: IProxyManager,
    mock_envs: None,
    database: None,
    test_demo_settings_generator: OverhaveDemoSettingsGenerator,
) -> IProxyManager:
    chdir(PROJECT_WORKDIR)
    _run_demo_admin(settings_generator=test_demo_settings_generator)
    return test_proxy_manager


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
def test_rendered_featureview() -> mock.MagicMock:
    return mock.create_autospec(werkzeug.Response)


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
