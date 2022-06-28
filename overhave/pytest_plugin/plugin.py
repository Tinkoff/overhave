import enum
import logging
from typing import Any, Callable, Dict, Optional

import _pytest
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Argument, Parser
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.python import Function
from pydantic import ValidationError
from pydantic.dataclasses import dataclass
from pytest_bdd.parser import Feature, Scenario, Step
from yarl import URL

from overhave.factory import IAdminFactory
from overhave.pytest_plugin.deps import get_description_manager, get_step_context_runner
from overhave.pytest_plugin.helpers import (
    add_admin_feature_link_to_report,
    add_scenario_title_to_report,
    add_task_links_to_report,
    get_feature_info_from_item,
    get_full_step_name,
    is_pytest_bdd_item,
    set_feature_info_for_item,
    set_git_project_url_if_necessary,
    set_severity_level,
)
from overhave.pytest_plugin.proxy_manager import get_proxy_manager

logger = logging.getLogger(__name__)


class StepNotFoundError(RuntimeError):
    """Exception for situation with missing or incorrect step definition."""


class _OptionName(str, enum.Enum):
    ENABLE_INJECTION = "--enable-injection"

    @property
    def as_variable(self) -> str:
        return self.value.lstrip("--").replace("-", "_")


_ENABLE_INJECTION_HELP = "Injection enabling of Overhave specified objects into PyTest session"
_FACTORY_CONTEXT_HELP = (
    "Relative path to lib with Overhave context definition for it's dynamical resolution before injection"
)


@dataclass(frozen=True)
class _Options:
    enable_injection = Argument(
        _OptionName.ENABLE_INJECTION.value,
        action="store_true",
        dest=_OptionName.ENABLE_INJECTION.as_variable,
        default=False,
        help=_ENABLE_INJECTION_HELP,
    )


_PLUGIN_NAME = "overhave-pytest"
_GROUP_HELP = "Overhave PyTest plugin commands"


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup(_PLUGIN_NAME, _GROUP_HELP)
    group.addoption(*_Options.enable_injection.names(), **_Options.enable_injection.attrs())


def pytest_configure(config: Config) -> None:
    """Patch pytest_bdd objects in current hook."""
    injection_enabled: bool = config.getoption(_OptionName.ENABLE_INJECTION.as_variable)
    tw = _pytest.config.create_terminal_writer(config)
    if injection_enabled:
        logger.debug("Got %s flag.", _OptionName.ENABLE_INJECTION)
        try:
            logger.debug("Try to patch pytest objects...")
            get_proxy_manager().patch_pytest()
            logger.debug("Successfully patched pytest objects.")
            tw.line("Overhave injector successfully initialized.", green=True)
        except ValidationError as e:
            tw.line(f"Could not initialize Overhave injector!\n{str(e)}", red=True)


def pytest_collection_modifyitems(session: Session) -> None:
    pytest_bdd_scenario_items = (item for item in session.items if is_pytest_bdd_item(item))
    for item in pytest_bdd_scenario_items:
        add_scenario_title_to_report(item)


def pytest_bdd_before_step(
    request: FixtureRequest, feature: Feature, scenario: Scenario, step: Step, step_func: Callable[[Any], None]
) -> None:
    get_step_context_runner.cache_clear()
    runner = get_step_context_runner()
    runner.set_title(get_full_step_name(step))
    runner.start()


def pytest_bdd_after_step(
    request: FixtureRequest,
    feature: Feature,
    scenario: Scenario,
    step: Step,
    step_func: Callable[[Any], None],
    step_func_args: Dict[str, Any],
) -> None:
    runner = get_step_context_runner()
    runner.stop(None)


def pytest_bdd_step_error(
    request: FixtureRequest,
    feature: Feature,
    scenario: Scenario,
    step: Step,
    step_func: Callable[[Any], None],
    step_func_args: Dict[str, Any],
    exception: BaseException,
) -> None:
    runner = get_step_context_runner()
    runner.stop(exception)


def pytest_bdd_apply_tag(tag: str, function: Function) -> Optional[bool]:
    if tag != "skip":
        return None
    marker = pytest.mark.skip(reason="Scenario manually marked as skipped")
    marker(function)
    return True


def pytest_bdd_step_func_lookup_error(
    request: FixtureRequest, feature: Feature, scenario: Scenario, step: Step, exception: BaseException
) -> None:
    raise StepNotFoundError(f"Could not found specified step '{get_full_step_name(step)}'") from exception


def pytest_collection_finish(session: Session) -> None:
    """Supplying of injector configs for steps collection."""
    proxy_manager = get_proxy_manager()
    if (
        session.config.getoption(_OptionName.ENABLE_INJECTION.as_variable)
        and proxy_manager.has_factory
        and isinstance(proxy_manager.factory, IAdminFactory)
    ):
        tw = _pytest.config.create_terminal_writer(session.config)
        if not proxy_manager.pytest_patched:
            tw.line("Could not supplement Overhave injector - pytest session has not been patched!", yellow=True)
            return
        try:
            proxy_manager.supply_injector_for_collection()
            tw.line("Overhave injector successfully supplemented.", green=True)
        except ValidationError as e:
            tw.line(f"Could not supplement Overhave injector!\n{str(e)}", red=True)
        proxy_manager.injector.adapt(session)


def pytest_runtest_setup(item: Item) -> None:
    """Hook for purgation of `get_description_manager` func and upgrading item for reports."""
    get_description_manager.cache_clear()
    if not is_pytest_bdd_item(item):
        return

    proxy_manager = get_proxy_manager()
    set_feature_info_for_item(item=item, scenario_parser=proxy_manager.factory.scenario_parser)
    feature_info = get_feature_info_from_item(item)

    admin_link_settings = proxy_manager.factory.context.admin_link_settings  # type: ignore
    if admin_link_settings.enabled and feature_info.id is not None:
        add_admin_feature_link_to_report(admin_link_settings=admin_link_settings, feature_id=feature_info.id)

    project_settings = proxy_manager.factory.context.project_settings
    if isinstance(project_settings.git_project_url, URL) and feature_info.type is not None:
        set_git_project_url_if_necessary(
            project_settings=project_settings,
            feature_extractor=proxy_manager.factory.feature_extractor,
            item=item,
            feature_type=feature_info.type,
        )
    if isinstance(project_settings.tasks_keyword, str) and feature_info.tasks:
        add_task_links_to_report(project_settings=project_settings, tasks=feature_info.tasks)

    set_severity_level(
        compilation_settings=proxy_manager.factory.context.compilation_settings,
        item=item,
    )


def pytest_runtest_teardown(item: Item, nextitem: Optional[Item]) -> None:
    """Hook for description attachment to Allure report."""
    get_description_manager().apply_description()
