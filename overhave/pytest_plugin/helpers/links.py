from pathlib import Path
from typing import List, Optional

import allure
import allure_commons.types
from _pytest.nodes import Item
from pytest_bdd.parser import Scenario

from overhave.pytest_plugin.helpers.bdd import get_scenario, is_pytest_bdd_item
from overhave.test_execution import OverhaveProjectSettings


def _get_issue_links(scenario: Scenario, keyword: str) -> Optional[List[str]]:
    keyword_with_colon = keyword.title() + ":"
    with Path(scenario.feature.filename).open() as feature_file:
        for line in feature_file:
            if keyword not in line:
                continue
            links_part = line.split(keyword_with_colon)[-1]
            return [x.strip() for x in links_part.split(",")]
    return None


def set_item_issue_links(item: Item, keyword: str) -> None:
    scenario = get_scenario(item)
    links = _get_issue_links(scenario, keyword)
    if links:
        setattr(scenario.feature, "links", links)


def has_issue_links(item: Item) -> bool:
    return is_pytest_bdd_item(item) and hasattr(get_scenario(item).feature, "links")


def add_issue_links_to_report(project_settings: OverhaveProjectSettings, scenario: Scenario) -> None:
    for link in getattr(scenario.feature, "links"):
        allure.dynamic.link(
            url=project_settings.get_link_url(link), link_type=allure_commons.types.LinkType.LINK, name=link
        )
