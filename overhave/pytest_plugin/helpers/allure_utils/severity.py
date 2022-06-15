from typing import Any, Optional

import allure
from _pytest.nodes import Item

from overhave.entities import OverhaveScenarioCompilerSettings
from overhave.pytest_plugin.helpers.parsed_info import get_feature_info_from_item


def _get_severity_level_from_tags(item: Item, keyword: str) -> Optional[allure.severity_level]:
    for marker in reversed(item.own_markers):
        if not marker.name.startswith(keyword):
            continue
        severity = marker.name.removeprefix(keyword)
        return allure.severity_level(severity)
    return None


def _get_parsed_feature_severity(item: Item, **kwargs: Any) -> Optional[allure.severity_level]:
    return get_feature_info_from_item(item).severity


def _get_default_severity(*args: Any, **kwargs: Any) -> allure.severity_level:
    return allure.severity_level.NORMAL


def set_severity_level(
    compilation_settings: OverhaveScenarioCompilerSettings,
    item: Item,
) -> None:
    for extractor_func in _get_severity_level_from_tags, _get_parsed_feature_severity, _get_default_severity:
        severity_lvl = extractor_func(item=item, keyword=compilation_settings.severity_keyword)  # type: ignore
        if severity_lvl is None:
            continue
        allure.dynamic.severity(severity_lvl)
        return
