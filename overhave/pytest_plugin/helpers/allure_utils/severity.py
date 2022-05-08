import allure
from _pytest.nodes import Item


def _get_severity_level(item: Item, keyword: str) -> allure.severity_level:
    for marker in item.own_markers:
        if not marker.name.startswith(keyword):
            continue
        severity = marker.name.removeprefix(keyword)
        return allure.severity_level(severity)
    return allure.severity_level.NORMAL


def set_severity_level(item: Item, keyword: str) -> None:
    parsed_severity = _get_severity_level(item, keyword)
    allure.dynamic.severity(parsed_severity)
