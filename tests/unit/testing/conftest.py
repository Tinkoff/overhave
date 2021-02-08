from typing import Optional, cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.python import Function
from faker import Faker
from pytest_bdd.parser import Feature, Scenario, Step

from overhave import OverhaveProjectSettings
from overhave.base_settings import OverhaveLoggingSettings
from overhave.factory import ProxyFactory
from overhave.testing.plugin_utils import StepContextRunner
from tests.objects import get_file_settings


@pytest.fixture(scope="session")
def test_clean_item() -> Item:
    return cast(Item, mock.MagicMock())


@pytest.fixture()
def test_scenario_name(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_pytest_bdd_scenario(test_scenario_name: str) -> Scenario:
    scenario = mock.create_autospec(Scenario)
    setattr(scenario, "feature", mock.create_autospec(Feature))
    setattr(
        scenario.feature,
        "filename",
        get_file_settings().features_base_dir / "feature_type_1" / "full_feature_example_en.feature",
    )
    setattr(scenario, "name", test_scenario_name)
    return scenario


@pytest.fixture()
def test_pytest_bdd_item(test_pytest_bdd_scenario: Scenario) -> Item:
    item = mock.create_autospec(Item)
    setattr(item, "_obj", mock.MagicMock())
    item._obj.__scenario__ = test_pytest_bdd_scenario
    return item


@pytest.fixture()
def test_pytest_bdd_step(faker: Faker) -> Step:
    item = mock.MagicMock()
    item.keyword = faker.word()
    item._name = faker.word()
    return cast(Step, item)


@pytest.fixture()
def test_browse_url(request: FixtureRequest) -> Optional[str]:
    if hasattr(request, "param"):
        return cast(Optional[str], request.param)
    raise NotImplementedError


@pytest.fixture()
def test_project_settings(test_browse_url: Optional[str]) -> OverhaveProjectSettings:
    return OverhaveProjectSettings(browse_url=test_browse_url)


@pytest.fixture()
def test_step_context_logs(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return cast(bool, request.param)
    raise NotImplementedError


@pytest.fixture()
def test_logging_settings(test_step_context_logs: bool) -> OverhaveLoggingSettings:
    return OverhaveLoggingSettings(step_context_logs=test_step_context_logs)


@pytest.fixture()
def test_step_context_runner(test_logging_settings: OverhaveLoggingSettings) -> StepContextRunner:
    return StepContextRunner(logging_settings=test_logging_settings)


@pytest.fixture()
def patched_proxy_factory() -> ProxyFactory:
    from overhave.factory import proxy_factory

    proxy_factory.set_context(mock.MagicMock())
    yield proxy_factory
    del proxy_factory


@pytest.fixture()
def clear_get_step_context_runner() -> None:
    from overhave.testing.plugin_utils import get_step_context_runner

    get_step_context_runner.cache_clear()


@pytest.fixture()
def test_pytest_function() -> Function:
    return mock.create_autospec(Function)
