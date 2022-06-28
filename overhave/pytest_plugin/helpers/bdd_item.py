import logging
from pathlib import Path

from _pytest.nodes import Item
from pytest_bdd.parser import Scenario, ScenarioTemplate, Step

from overhave.entities import IFeatureExtractor
from overhave.pytest_plugin.helpers.allure_utils import add_git_project_feature_link_to_report
from overhave.storage import FeatureTypeName
from overhave.test_execution import OverhaveProjectSettings

logger = logging.getLogger(__name__)


def get_scenario(item: Item) -> Scenario:
    return item._obj.__scenario__  # type: ignore


def add_scenario_title_to_report(item: Item) -> None:
    item._obj.__allure_display_name__ = get_scenario(item).name  # type: ignore


def is_pytest_bdd_item(item: Item) -> bool:
    if hasattr(item, "_obj"):
        return hasattr(item._obj, "__scenario__") and isinstance(  # type: ignore
            get_scenario(item), (Scenario, ScenarioTemplate)
        )
    return False


def get_full_step_name(step: Step) -> str:
    return f"{step.keyword} {step._name}"


def set_git_project_url_if_necessary(
    project_settings: OverhaveProjectSettings,
    feature_extractor: IFeatureExtractor,
    item: Item,
    feature_type: FeatureTypeName,
) -> None:
    scenario = get_scenario(item)
    filename = Path(scenario.feature.filename)
    feature_type_dir = feature_extractor.feature_type_to_dir_mapping[feature_type]
    if not filename.is_relative_to(feature_type_dir):
        logger.warning("pytest_bdd item file '%s' is not relative to '%s'!")
        return
    relative_path = filename.relative_to(feature_type_dir.parent)
    add_git_project_feature_link_to_report(project_settings=project_settings, filepath=relative_path)
