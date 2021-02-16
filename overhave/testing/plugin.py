import enum
import logging
from typing import Any, Callable, Dict, Optional, cast

import _pytest
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Argument, Parser
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.python import Function
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from pydantic import ValidationError
from pydantic.dataclasses import dataclass
from pytest_bdd.parser import Feature, Scenario, Step

from overhave.factory import get_proxy_factory
from overhave.testing.plugin_utils import (
    add_issue_links_to_report,
    add_scenario_title_to_report,
    get_description_manager,
    get_full_step_name,
    get_scenario,
    get_step_context_runner,
    has_issue_links,
    is_pytest_bdd_item,
    set_issue_links,
)

logger = logging.getLogger(__name__)


class StepNotFoundError(RuntimeError):
    """ Exception for situation with missing or incorrect step definition. """


class _OptionName(str, enum.Enum):
    ENABLE_INJECTION = "--enable-injection"
    FACTORY_CONTEXT = "--ctx-module"

    @property
    def as_variable(self) -> str:
        return cast(str, self.value.lstrip("--").replace("-", "_"))


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
    context_module = Argument(
        _OptionName.FACTORY_CONTEXT.value,
        action="store",
        dest=_OptionName.FACTORY_CONTEXT.as_variable,
        default=None,
        help=_FACTORY_CONTEXT_HELP,
    )


_PLUGIN_NAME = "overhave-pytest"
_GROUP_HELP = "Overhave PyTest plugin commands"


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup(_PLUGIN_NAME, _GROUP_HELP)
    group.addoption(*_Options.enable_injection.names(), **_Options.enable_injection.attrs())
    group.addoption(*_Options.context_module.names(), **_Options.context_module.attrs())


def pytest_configure(config: Config) -> None:
    """ Patch pytest_bdd objects in current hook. """
    injection_enabled: bool = config.getoption(_OptionName.ENABLE_INJECTION.as_variable)
    factory_context_path: Optional[str] = config.getoption(_OptionName.FACTORY_CONTEXT.as_variable)
    tw = _pytest.config.create_terminal_writer(config)
    if factory_context_path is not None and not injection_enabled:
        tw.line("Got path for context definition, but injection is disabled!", yellow=True)
        return
    if injection_enabled:
        logger.debug("Got %s flag.", _OptionName.ENABLE_INJECTION)
        try:
            if factory_context_path is not None:
                logger.debug("Factory context path: %s", factory_context_path)
                import importlib

                importlib.import_module(factory_context_path)
            logger.debug("Try to patch pytest objects...")
            get_proxy_factory().patch_pytest()
            logger.debug("Successfully patched pytest objects.")
            tw.line("Overhave injector successfully initialized.", green=True)
        except ValidationError as e:
            tw.line(f"Could not initialize Overhave injector!\n{str(e)}", red=True)


def pytest_collection_modifyitems(session: Session) -> None:
    pytest_bdd_scenario_items = (item for item in session.items if is_pytest_bdd_item(item))
    for item in pytest_bdd_scenario_items:
        add_scenario_title_to_report(item)

        links_keyword = get_proxy_factory().context.project_settings.links_keyword
        if isinstance(links_keyword, str):
            set_issue_links(scenario=get_scenario(item), keyword=links_keyword)


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
    if tag != 'skip':
        return None
    marker = pytest.mark.skip(reason="Scenario manually marked as skipped")
    marker(function)
    return True


def pytest_bdd_step_func_lookup_error(
    request: FixtureRequest, feature: Feature, scenario: Scenario, step: Step, exception: BaseException
) -> None:
    raise StepNotFoundError(f"Could not found specified step '{get_full_step_name(step)}'") from exception


def pytest_collection_finish(session: Session) -> None:
    """ Supplying of injector configs for steps collection. """
    if session.config.getoption(_OptionName.ENABLE_INJECTION.as_variable):
        tw = _pytest.config.create_terminal_writer(session.config)
        factory = get_proxy_factory()
        if not factory.pytest_patched:
            tw.line("Could not supplement Overhave injector - pytest session has not been patched!", yellow=True)
            return
        try:
            factory.supply_injector_for_collection()
            tw.line("Overhave injector successfully supplemented.", green=True)
        except ValidationError as e:
            tw.line(f"Could not supplement Overhave injector!\n{str(e)}", red=True)
        factory.injector.adapt(session)


def pytest_runtest_setup(item: Item) -> None:
    """ Hook for purgation of get_description_manager. """
    get_description_manager.cache_clear()


def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> Optional[TestReport]:
    """ Hook for description and issue links attachment to Allure report. """
    get_description_manager().apply_description()
    factory = get_proxy_factory()
    if all((factory.context.project_settings.browse_url is not None, has_issue_links(item))):
        add_issue_links_to_report(project_settings=factory.context.project_settings, scenario=get_scenario(item))
    return None  # noqa: R501
