from typing import Optional, cast
from unittest import mock

import pytest
from _pytest.config import Config, PytestPluginManager
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.python import Function
from faker import Faker
from pytest_bdd.parser import Feature, Scenario, Step

from overhave import OverhaveDescriptionManagerSettings, OverhaveProjectSettings
from overhave.base_settings import OverhaveLoggingSettings
from overhave.factory import ProxyFactory
from overhave.testing.plugin import pytest_addoption
from overhave.testing.plugin_utils import DescriptionManager, StepContextRunner
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


@pytest.fixture()
def test_blocks_delimiter(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_description_manager_settings(test_blocks_delimiter: str) -> OverhaveDescriptionManagerSettings:
    return OverhaveDescriptionManagerSettings(blocks_delimiter=test_blocks_delimiter)


@pytest.fixture()
def test_description_manager(
    test_description_manager_settings: OverhaveDescriptionManagerSettings,
) -> DescriptionManager:
    return DescriptionManager(settings=test_description_manager_settings)


@pytest.fixture()
def description_handler_mock() -> mock.MagicMock:
    with mock.patch("allure.dynamic.description_html", return_value=mock.MagicMock()) as mocked_description_handler:
        yield mocked_description_handler


@pytest.fixture()
def clear_get_description_manager() -> None:
    from overhave.testing.plugin_utils import get_description_manager

    get_description_manager.cache_clear()


@pytest.fixture()
def test_pytest_parser() -> Parser:
    return Parser()


@pytest.fixture(scope="session")
def test_empty_config() -> Config:
    return Config(PytestPluginManager())


@pytest.fixture()
def terminal_writer_mock() -> mock.MagicMock:
    with mock.patch("_pytest.config.create_terminal_writer", return_value=mock.MagicMock()) as terminal_writer:
        yield terminal_writer


@pytest.fixture()
def import_module_mock() -> mock.MagicMock:
    with mock.patch("importlib.import_module", return_value=mock.MagicMock()) as import_module:
        yield import_module


@pytest.fixture()
def test_prepared_config(terminal_writer_mock: mock.MagicMock, import_module_mock: mock.MagicMock) -> Config:
    config = Config(PytestPluginManager())
    test_pytest_parser = Parser(
        usage="%(prog)s [options] [file_or_dir] [file_or_dir] [...]", processopt=config._processopt
    )
    pytest_addoption(test_pytest_parser)
    config._parser = test_pytest_parser
    return config
