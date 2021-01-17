from pathlib import Path
from typing import List, Optional

import allure
from _pytest.nodes import Item
from pytest_bdd.parser import Scenario

from overhave.factory import IOverhaveFactory


def _get_issue_links(item: Scenario, keyword: str) -> Optional[List[str]]:
    keyword_with_colon = keyword.title() + ":"
    with Path(item._obj.__scenario__.feature.filename).open() as file:
        for line in file:
            if keyword not in line:
                continue
            links_part = line.split(keyword_with_colon)[-1]
            return [x.strip() for x in links_part.split(",")]
    return None


def set_issue_links(item: Scenario, keyword: str) -> None:
    links = _get_issue_links(item, keyword)
    if links:
        setattr(item._obj.__scenario__.feature, "links", links)


def is_pytest_bdd_item(item: Item) -> bool:
    if hasattr(item, "_obj"):
        return hasattr(item._obj, "__scenario__") and isinstance(item._obj.__scenario__, Scenario)  # type: ignore
    return False


def has_issue_links(item: Item) -> bool:
    return is_pytest_bdd_item(item) and hasattr(item._obj.__scenario__.feature, "links")  # type: ignore


def add_issue_links_to_report(factory: IOverhaveFactory, item: Scenario) -> None:
    for link in item._obj.__scenario__.feature.links:
        allure.dynamic.link(url=factory.context.project_settings.get_link_url(link), name=link)
