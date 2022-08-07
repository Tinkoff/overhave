from functools import cache

from overhave.pytest_plugin.helpers import OverhaveTagController
from overhave.pytest_plugin.helpers.allure_utils.description_manager import DescriptionManager
from overhave.pytest_plugin.helpers.allure_utils.step_context_runner import StepContextRunner


@cache
def get_step_context_runner() -> StepContextRunner:
    from overhave.factory import get_test_execution_factory

    return StepContextRunner(settings=get_test_execution_factory().context.step_context_settings)


@cache
def get_description_manager() -> DescriptionManager:
    from overhave.factory import get_test_execution_factory

    return DescriptionManager(settings=get_test_execution_factory().context.description_manager_settings)


@cache
def get_tag_controller() -> OverhaveTagController:
    return OverhaveTagController()
