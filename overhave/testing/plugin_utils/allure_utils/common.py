from functools import lru_cache

from _pytest.nodes import Item

from overhave.testing.plugin_utils.allure_utils.description_manager import DescriptionManager
from overhave.testing.plugin_utils.allure_utils.step_context_runner import StepContextRunner
from overhave.testing.plugin_utils.basic import get_scenario


def add_scenario_title_to_report(item: Item) -> None:
    item._obj.__allure_display_name__ = get_scenario(item).name  # type: ignore


@lru_cache(maxsize=None)
def get_step_context_runner() -> StepContextRunner:
    from overhave.factory import get_proxy_factory

    return StepContextRunner(logging_settings=get_proxy_factory().context.logging_settings)


@lru_cache(maxsize=None)
def get_description_manager() -> DescriptionManager:
    from overhave.factory import get_proxy_factory

    return DescriptionManager(settings=get_proxy_factory().context.description_manager_settings)
