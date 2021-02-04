import enum
import importlib
import logging
from typing import Any, Optional, cast

import _pytest
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.nodes import Item
from pydantic import ValidationError

from overhave.factory import proxy_factory
from overhave.testing.plugin_utils import (
    add_issue_links_to_report,
    add_scenario_title_to_report,
    get_scenario,
    has_issue_links,
    is_pytest_bdd_item,
    set_issue_links,
)

logger = logging.getLogger(__name__)


class _Options(str, enum.Enum):
    ENABLE_INJECTION = "--enable-injection"
    FACTORY_CONTEXT = "--ctx-module"

    @property
    def as_variable(self) -> str:
        return cast(str, self.value.lstrip("--").replace("-", "_"))


_ENABLE_INJECTION_HELP = "Injection enabling of Overhave specified objects into PyTest session"
_FACTORY_CONTEXT_HELP = (
    "Relative path to lib with Overhave context definition for it's dynamical resolution before injection"
)


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("overhave-pytest", "Overhave PyTest plugin commands")
    group.addoption(
        _Options.ENABLE_INJECTION,
        action="store_true",
        dest=_Options.ENABLE_INJECTION.as_variable,
        default=False,
        help=_ENABLE_INJECTION_HELP,
    )
    group.addoption(
        _Options.FACTORY_CONTEXT,
        action="store",
        dest=_Options.FACTORY_CONTEXT.as_variable,
        default=None,
        help=_FACTORY_CONTEXT_HELP,
    )


def pytest_configure(config: Any) -> None:
    """ Patch pytest_bdd objects in current hook. """
    factory_context_path: Optional[str] = config.getoption(_Options.FACTORY_CONTEXT.as_variable)
    injection_enabled: bool = config.getoption(_Options.ENABLE_INJECTION.as_variable)
    tw = _pytest.config.create_terminal_writer(config)
    if factory_context_path is not None and not injection_enabled:
        tw.line("Got path for context definition, but injection is disabled!", yellow=True)
        return
    if injection_enabled:
        logger.debug("Got %s flag.", _Options.ENABLE_INJECTION)
        try:
            if factory_context_path is not None:
                logger.debug("Factory context path: %s", factory_context_path)
                importlib.import_module(factory_context_path)
            logger.debug("Try to patch pytest objects...")
            proxy_factory.patch_pytest()
            logger.debug("Successfully patched pytest objects.")
            tw.line("Overhave injector successfully initialized.", green=True)
        except ValidationError as e:
            tw.line(f"Could not initialize Overhave injector!\n{str(e)}", red=True)


def pytest_collection_modifyitems(session: Session) -> None:
    browse_url = proxy_factory.context.project_settings.browse_url
    pytest_bdd_scenario_items = (item for item in session.items if is_pytest_bdd_item(item))
    for item in pytest_bdd_scenario_items:
        add_scenario_title_to_report(item)
        if browse_url is not None:
            set_issue_links(scenario=get_scenario(item), keyword=browse_url.human_repr())


def pytest_collection_finish(session: Session) -> None:
    """ Supplying of injector configs for steps collection. """
    if session.config.getoption(_Options.ENABLE_INJECTION.as_variable):
        tw = _pytest.config.create_terminal_writer(session.config)
        if not proxy_factory.pytest_patched:
            tw.line("Could not supplement Overhave injector - pytest session has not been patched!", yellow=True)
            return
        try:
            proxy_factory.supply_injector_for_collection()
            tw.line("Overhave injector successfully supplemented.", green=True)
        except ValidationError as e:
            tw.line(f"Could not supplement Overhave injector!\n{str(e)}", red=True)
        proxy_factory.injector.adapt(session)


def pytest_runtest_teardown(item: Item) -> None:
    """ Hook for issue links attachment. """
    if all((proxy_factory.context.project_settings.browse_url is not None, has_issue_links(item))):
        add_issue_links_to_report(project_settings=proxy_factory.context.project_settings, scenario=get_scenario(item))
