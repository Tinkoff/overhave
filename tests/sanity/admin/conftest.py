from os import chdir
from typing import Any, Callable, Dict, List, cast
from unittest import mock

import pytest
import werkzeug
from _pytest.fixtures import FixtureRequest
from flask import Flask
from pytest_mock import MockFixture

from demo.demo import _run_demo_admin
from overhave.admin.views import FeatureView
from overhave.admin.views.feature import _SCENARIO_PREFIX
from overhave.entities import ScenarioModel, SystemUserModel
from overhave.factory import IAdminFactory
from overhave.pytest_plugin import IProxyManager
from tests.objects import PROJECT_WORKDIR


@pytest.fixture()
def flask_run_mock() -> mock.MagicMock:
    with mock.patch.object(Flask, "run", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler


@pytest.fixture(scope="module")
def test_feature_types() -> List[str]:
    return ["feature_type_1", "feature_type_2", "feature_type_3"]


@pytest.fixture()
def test_admin_factory(clean_admin_factory: Callable[[], IAdminFactory]) -> IAdminFactory:
    return clean_admin_factory()


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
