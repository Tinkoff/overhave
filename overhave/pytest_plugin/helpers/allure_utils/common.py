from typing import List

import allure
import allure_commons.types
from _pytest.nodes import Item

from overhave.pytest_plugin.helpers.bdd_item import get_scenario
from overhave.test_execution import OverhaveProjectSettings


def add_scenario_title_to_report(item: Item) -> None:
    item._obj.__allure_display_name__ = get_scenario(item).name  # type: ignore


def add_task_links_to_report(project_settings: OverhaveProjectSettings, tasks: List[str]) -> None:
    for task in tasks:
        allure.dynamic.link(
            url=project_settings.get_link_url(task), link_type=allure_commons.types.LinkType.LINK, name=task
        )
