import logging
from typing import Any, Callable, Dict, Optional

import _pytest
import allure
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.python import Function
from pydantic import ValidationError
from pytest_bdd.parser import Feature, Scenario, Step
from yarl import URL

from overhave.factory import IAdminFactory
from overhave.pytest_plugin.deps import get_description_manager, get_step_context_runner, get_tag_controller
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


def pytest_configure(config: Config) -> None:
    """Patch pytest_bdd objects in current hook."""
    proxy_manager = get_proxy_manager()
    if not proxy_manager.has_factory:
        logger.debug("Overhave ProxyManager has not got prepared factory, so skip injection.")
        return
    tw = _pytest.config.create_terminal_writer(config)
    try:
        logger.debug("Try to patch pytest objects...")
        proxy_manager.patch_pytest()
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
    controller = get_tag_controller()
    tag_pattern = controller.get_suitable_pattern(tag)
    if not tag_pattern:
        logger.debug("Tag '%s' is not suitable for evaluation", tag)
        return None
    result = controller.evaluate_tag(name=tag, pattern=tag_pattern)
    result.marker(function)
    if result.url is not None:
        allure.dynamic.link(url=result.url, link_type=result.link_type, name=result.url)
    logger.debug("Tag '%s' successfully evaluated")
    return True


def pytest_bdd_step_func_lookup_error(
    request: FixtureRequest, feature: Feature, scenario: Scenario, step: Step, exception: BaseException
) -> None:
    raise StepNotFoundError(f"Could not found specified step '{get_full_step_name(step)}'") from exception


def pytest_collection_finish(session: Session) -> None:
    """Supplying of injector configs for steps collection (only :class:`IAdminFactory`)."""
    proxy_manager = get_proxy_manager()
    if not proxy_manager.has_factory or not isinstance(proxy_manager.factory, IAdminFactory):
        return
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
    proxy_manager = get_proxy_manager()
    if not proxy_manager.has_factory or not is_pytest_bdd_item(item):
        return

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
    if not get_proxy_manager().has_factory:
        return
    get_description_manager().apply_description()
