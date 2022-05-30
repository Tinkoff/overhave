import re
from functools import cache
from pathlib import Path
from typing import Any, Optional, Pattern

import allure
from _pytest.nodes import Item

from overhave.pytest_plugin.helpers.bdd import get_scenario


def _get_severity_level_from_tags(item: Item, keyword: str) -> Optional[allure.severity_level]:
    for marker in reversed(item.own_markers):
        if not marker.name.startswith(keyword):
            continue
        severity = marker.name.removeprefix(keyword)
        return allure.severity_level(severity)
    return None


@cache
def _get_severity_pattern(keyword: str) -> Pattern[str]:
    return re.compile(rf"({keyword})(?P<severity>\w+)\b")


def _get_severity_level_from_feature(item: Item, keyword: str) -> Optional[allure.severity_level]:
    scenario = get_scenario(item)
    with Path(scenario.feature.filename).open() as feature_file:
        head_line = next(iter(feature_file))
        parsed_severity = _get_severity_pattern(keyword).search(head_line)
        if parsed_severity is not None:
            return allure.severity_level(parsed_severity.group("severity"))
    return None


def _get_default_severity(*args: Any, **kwargs: Any) -> allure.severity_level:
    return allure.severity_level.NORMAL


def set_severity_level(item: Item, keyword: str) -> None:
    for extractor_func in _get_severity_level_from_tags, _get_severity_level_from_feature, _get_default_severity:
        parsed_severity = extractor_func(*(item, keyword))  # type: ignore
        if parsed_severity is None:
            continue
        allure.dynamic.severity(parsed_severity)
        return
