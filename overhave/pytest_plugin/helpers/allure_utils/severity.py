from typing import TextIO

import allure


def _get_severity_level(file_wrapper: TextIO, keyword: str) -> allure.severity_level:
    for line in file_wrapper:
        if keyword not in line:
            continue
        severity = line.split(keyword)[-1]
        return allure.severity_level(severity.strip())
    return allure.severity_level.NORMAL


def set_severity_level(file_wrapper: TextIO, keyword: str) -> None:
    parsed_severity = _get_severity_level(file_wrapper, keyword)
    allure.dynamic.severity(parsed_severity)
