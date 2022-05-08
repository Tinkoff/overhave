import re
from functools import cache
from typing import Pattern, TextIO

import allure


@cache
def _get_severity_pattern(keyword: str) -> Pattern[str]:
    return re.compile(rf"({keyword})(?P<severity>\w+)\b")


def _get_severity_level(file_wrapper: TextIO, keyword: str) -> allure.severity_level:
    for line in file_wrapper:
        if keyword not in line:
            continue
        parsed_severity = _get_severity_pattern(keyword).search(line)
        if parsed_severity is not None:
            return allure.severity_level(parsed_severity.group("severity"))
    return allure.severity_level.NORMAL


def set_severity_level(file_wrapper: TextIO, keyword: str) -> None:
    parsed_severity = _get_severity_level(file_wrapper, keyword)
    allure.dynamic.severity(parsed_severity)
