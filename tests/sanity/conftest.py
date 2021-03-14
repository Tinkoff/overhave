from os import chdir
from typing import Callable, Dict, List, Optional, cast
from unittest import mock

import click
import pytest
from flask import Flask

from demo.demo import _run_demo_admin
from overhave import db, set_config_to_context
from overhave.base_settings import DataBaseSettings
from overhave.entities import ScenarioModel, SystemUserModel
from overhave.factory import ProxyFactory
from overhave.processing import Processor
from tests.objects import PROJECT_WORKDIR, FeatureTestContainer


@pytest.fixture(scope="module")
def envs_for_mock(db_settings: DataBaseSettings) -> Dict[str, Optional[str]]:
    return {
        "OVERHAVE_DB_URL": str(db_settings.db_url),
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def flask_run_mock(mock_envs: None, database: None) -> mock.MagicMock:
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
def test_proxy_factory(clean_proxy_factory: Callable[[], ProxyFactory]) -> ProxyFactory:
    return clean_proxy_factory()


@pytest.fixture()
def test_resolved_factory(flask_run_mock: mock.MagicMock, test_proxy_factory: ProxyFactory) -> ProxyFactory:
    chdir(PROJECT_WORKDIR)
    _run_demo_admin()
    return test_proxy_factory


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
def flask_urlfor_handler_mock(test_db_scenario: ScenarioModel) -> mock.MagicMock:
    with mock.patch("flask.url_for", return_value=f"/testrun/details/?id={test_db_scenario.id}") as flask_run_handler:
        yield flask_run_handler


def synchronous_apply(*args, **kwargs) -> None:
    func = args[0]
    func_args = kwargs.get("args")
    func(*func_args)


@pytest.fixture()
def patched_threadpool_apply_async(test_resolved_factory: ProxyFactory) -> mock.MagicMock:
    processor = cast(Processor, test_resolved_factory.processor)
    with mock.patch.object(
        processor._thread_pool, "apply_async", new_callable=lambda: synchronous_apply
    ) as patched_threadpool:
        yield patched_threadpool


@pytest.fixture(scope="module")
def subprocess_run_mock() -> mock.MagicMock:
    returncode_mock = mock.MagicMock()
    returncode_mock.returncode = 0
    with mock.patch("subprocess.run", return_value=returncode_mock) as mocked_subprocess_run:
        yield mocked_subprocess_run


@pytest.fixture()
def test_factory_after_run(
    subprocess_run_mock: mock.MagicMock,
    test_resolved_factory: ProxyFactory,
    test_db_user: SystemUserModel,
    test_db_scenario: ScenarioModel,
    flask_urlfor_handler_mock: mock.MagicMock,
    patched_threadpool_apply_async: mock.MagicMock,
) -> ProxyFactory:
    test_resolved_factory.processor.execute_test(scenario_id=test_db_scenario.id, executed_by=test_db_user.login)
    return test_resolved_factory
