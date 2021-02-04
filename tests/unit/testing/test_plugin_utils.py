from typing import Optional

import pytest
from _pytest.nodes import Item
from pytest_bdd.parser import Scenario

from overhave import OverhaveProjectSettings
from overhave.testing import (
    EmptyBrowseURLError,
    add_issue_links_to_report,
    add_scenario_title_to_report,
    get_scenario,
    has_issue_links,
    is_pytest_bdd_item,
    set_issue_links,
)


class TestPluginUtils:
    """ Unit tests for plugin utils. """

    def test_get_scenario(self, test_pytest_bdd_scenario: Scenario, test_pytest_bdd_item: Item):
        assert test_pytest_bdd_scenario == get_scenario(test_pytest_bdd_item)

    def test_correct_pytest_bdd_item(self, test_pytest_bdd_item: Item):
        assert is_pytest_bdd_item(test_pytest_bdd_item)

    def test_not_pytest_bdd_item(self, test_clean_item: Item):
        assert not is_pytest_bdd_item(test_clean_item)

    @pytest.mark.parametrize("keyword", ["Tasks"])
    def test_issue_links_with_correct_keyword(self, test_pytest_bdd_item: Item, keyword: str):
        scenario = get_scenario(test_pytest_bdd_item)
        set_issue_links(scenario=scenario, keyword=keyword)
        assert hasattr(get_scenario(test_pytest_bdd_item).feature, "links")
        assert set(getattr(get_scenario(test_pytest_bdd_item).feature, "links")) == {"PRJ-1234", "PRJ-1235"}
        assert has_issue_links(test_pytest_bdd_item)

    @pytest.mark.parametrize("keyword", ["Trash"])
    def test_issue_links_with_incorrect_keyword(self, test_pytest_bdd_item: Item, keyword: str):
        scenario = get_scenario(test_pytest_bdd_item)
        set_issue_links(scenario=scenario, keyword=keyword)
        assert not hasattr(get_scenario(test_pytest_bdd_item).feature, "links")
        assert not has_issue_links(test_pytest_bdd_item)

    @pytest.mark.parametrize("keyword", ["Tasks"])
    @pytest.mark.parametrize("test_browse_url", ["https://overhave.readthedocs.io/"], indirect=True)
    def test_add_issue_links_to_report_with_correct_browse_url(
        self,
        test_pytest_bdd_item: Item,
        keyword: str,
        test_browse_url: Optional[str],
        test_project_settings: OverhaveProjectSettings,
    ):
        scenario = get_scenario(test_pytest_bdd_item)
        set_issue_links(scenario=scenario, keyword=keyword)
        add_issue_links_to_report(project_settings=test_project_settings, scenario=scenario)

    @pytest.mark.parametrize("keyword", ["Tasks"])
    @pytest.mark.parametrize("test_browse_url", [None], indirect=True)
    def test_add_issue_links_to_report_with_empty_browse_url(
        self,
        test_pytest_bdd_item: Item,
        keyword: str,
        test_browse_url: Optional[str],
        test_project_settings: OverhaveProjectSettings,
    ):
        scenario = get_scenario(test_pytest_bdd_item)
        set_issue_links(scenario=scenario, keyword=keyword)
        with pytest.raises(EmptyBrowseURLError):
            add_issue_links_to_report(project_settings=test_project_settings, scenario=scenario)

    def test_add_scenario_title_to_report(self, test_scenario_name: str, test_pytest_bdd_item: Item):
        allure_attr = "__allure_display_name__"
        assert not hasattr(test_pytest_bdd_item._obj, allure_attr)
        add_scenario_title_to_report(test_pytest_bdd_item)
        assert hasattr(test_pytest_bdd_item._obj, allure_attr)
        assert getattr(test_pytest_bdd_item._obj, allure_attr) == test_scenario_name
