from functools import lru_cache

from _pytest.nodes import Item

from overhave.pytest_plugin.helpers.allure_utils.description_manager import DescriptionManager
from overhave.pytest_plugin.helpers.allure_utils.step_context_runner import StepContextRunner
from overhave.pytest_plugin.helpers.basic import get_scenario


def add_scenario_title_to_report(item: Item) -> None:
    item._obj.__allure_display_name__ = get_scenario(item).name  # type: ignore


@lru_cache(maxsize=None)
def get_step_context_runner() -> StepContextRunner:
    from overhave.factory import get_test_execution_factory

    return StepContextRunner(settings=get_test_execution_factory().context.step_context_settings)


@lru_cache(maxsize=None)
def get_description_manager() -> DescriptionManager:
    from overhave.factory import get_test_execution_factory

    return DescriptionManager(settings=get_test_execution_factory().context.description_manager_settings)
