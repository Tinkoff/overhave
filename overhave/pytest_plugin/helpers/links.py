from typing import List, Optional, TextIO

import allure
import allure_commons.types
from _pytest.nodes import Item
from pytest_bdd.parser import Scenario

from overhave.pytest_plugin.helpers.basic import get_scenario, is_pytest_bdd_item
from overhave.test_execution import OverhaveProjectSettings


def _get_issue_links(file_wrapper: TextIO, keyword: str) -> Optional[List[str]]:
    keyword_with_colon = keyword.title() + ":"
    for line in file_wrapper:
        if keyword not in line:
            continue
        links_part = line.split(keyword_with_colon)[-1]
        return [x.strip() for x in links_part.split(",")]
    return None


def set_issue_links(file_wrapper: TextIO, scenario: Scenario, keyword: str) -> None:
    links = _get_issue_links(file_wrapper, keyword)
    if links:
        setattr(scenario.feature, "links", links)


def has_issue_links(item: Item) -> bool:
    return is_pytest_bdd_item(item) and hasattr(get_scenario(item).feature, "links")


def add_issue_links_to_report(project_settings: OverhaveProjectSettings, scenario: Scenario) -> None:
    for link in scenario.feature.links:
        allure.dynamic.link(
            url=project_settings.get_link_url(link), link_type=allure_commons.types.LinkType.LINK, name=link
        )
