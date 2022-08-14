from pathlib import Path
from typing import Optional, cast

from _pytest.nodes import Item
from pytest_bdd.parser import Scenario

from overhave.pytest_plugin.helpers.bdd_item import get_scenario
from overhave.scenario import FeatureInfo, ScenarioParser


def _parse_feature_info_from_file(scenario: Scenario, scenario_parser: ScenarioParser) -> FeatureInfo:
    feature_txt = Path(scenario.feature.filename).read_text()
    return cast(FeatureInfo, scenario_parser.parse(feature_txt))


def set_feature_info_for_item(item: Item, scenario_parser: ScenarioParser) -> None:
    setattr(
        item,
        "feature_info",
        _parse_feature_info_from_file(scenario=get_scenario(item), scenario_parser=scenario_parser),
    )


def get_feature_info_from_item(item: Item) -> FeatureInfo:
    feature_info: Optional[FeatureInfo] = getattr(item, "feature_info")
    if feature_info is None:
        raise AttributeError(f"Item {item} has not got attr 'feature_info'!")
    return feature_info
