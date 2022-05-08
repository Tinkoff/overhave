from typing import Optional
from unittest import mock

import allure
import pytest
from _pytest.nodes import Item
from pytest_bdd.parser import Scenario, Step

from overhave.factory.context.base_context import BaseFactoryContext
from overhave.pytest_plugin import get_scenario, has_issue_links
from overhave.pytest_plugin.helpers import (
    add_issue_links_to_report,
    add_scenario_title_to_report,
    get_full_step_name,
    is_pytest_bdd_item,
    set_issue_links,
    set_severity_level,
)
from overhave.test_execution.settings import EmptyBrowseURLError, OverhaveProjectSettings


class TestPluginUtils:
    """Unit tests for plugin utils."""

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_scenario(self, test_pytest_bdd_scenario: Scenario, test_pytest_bdd_item: Item) -> None:
        assert test_pytest_bdd_scenario == get_scenario(test_pytest_bdd_item)

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_correct_pytest_bdd_item(self, test_pytest_bdd_item: Item) -> None:
        assert is_pytest_bdd_item(test_pytest_bdd_item)

    def test_not_pytest_bdd_item(self, test_clean_item: Item) -> None:
        assert not is_pytest_bdd_item(test_clean_item)

    @pytest.mark.parametrize("keyword", ["Tasks"])
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_issue_links_with_correct_keyword(self, test_pytest_bdd_item: Item, keyword: str) -> None:
        set_issue_links(item=test_pytest_bdd_item, keyword=keyword)
        assert hasattr(get_scenario(test_pytest_bdd_item).feature, "links")
        assert set(getattr(get_scenario(test_pytest_bdd_item).feature, "links")) == {"PRJ-1234", "PRJ-1235"}
        assert has_issue_links(test_pytest_bdd_item)

    @pytest.mark.parametrize("keyword", ["Trash"])
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_issue_links_with_incorrect_keyword(self, test_pytest_bdd_item: Item, keyword: str) -> None:
        set_issue_links(item=test_pytest_bdd_item, keyword=keyword)
        assert not hasattr(get_scenario(test_pytest_bdd_item).feature, "links")
        assert not has_issue_links(test_pytest_bdd_item)

    @pytest.mark.parametrize("keyword", ["Tasks"])
    @pytest.mark.parametrize("test_browse_url", ["https://overhave.readthedocs.io/"], indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_add_issue_links_to_report_with_correct_browse_url(
        self,
        test_pytest_bdd_item: Item,
        keyword: str,
        test_browse_url: Optional[str],
        test_project_settings: OverhaveProjectSettings,
    ) -> None:
        set_issue_links(item=test_pytest_bdd_item, keyword=keyword)
        add_issue_links_to_report(project_settings=test_project_settings, scenario=get_scenario(test_pytest_bdd_item))

    @pytest.mark.parametrize("keyword", ["Tasks"])
    @pytest.mark.parametrize("test_browse_url", [None], indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_add_issue_links_to_report_with_empty_browse_url(
        self,
        test_pytest_bdd_item: Item,
        keyword: str,
        test_browse_url: Optional[str],
        test_project_settings: OverhaveProjectSettings,
    ) -> None:
        set_issue_links(item=test_pytest_bdd_item, keyword=keyword)
        with pytest.raises(EmptyBrowseURLError):
            add_issue_links_to_report(
                project_settings=test_project_settings, scenario=get_scenario(test_pytest_bdd_item)
            )

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_add_scenario_title_to_report(self, test_scenario_name: str, test_pytest_bdd_item: Item) -> None:
        allure_attr = "__allure_display_name__"
        item_obj = getattr(test_pytest_bdd_item, "_obj")
        assert not hasattr(item_obj, allure_attr)
        add_scenario_title_to_report(test_pytest_bdd_item)
        assert hasattr(item_obj, allure_attr)
        assert getattr(item_obj, allure_attr) == test_scenario_name

    def test_get_full_step_name(self, test_pytest_bdd_step: Step) -> None:
        assert (
            get_full_step_name(test_pytest_bdd_step) == f"{test_pytest_bdd_step.keyword} {test_pytest_bdd_step._name}"
        )

    @pytest.mark.parametrize("test_severity", list(allure.severity_level), indirect=True)
    @pytest.mark.parametrize("severity_keyword", ["yet_another_keyword"])
    def test_set_severity_not_match_keyword(
        self,
        test_pytest_bdd_item: Item,
        severity_keyword: str,
        severity_handler_mock: mock.MagicMock,
    ) -> None:
        set_severity_level(item=test_pytest_bdd_item, keyword=severity_keyword)
        assert severity_handler_mock.called_once(allure.severity_level.NORMAL)

    @pytest.mark.parametrize("test_severity", list(allure.severity_level), indirect=True)
    def test_set_severity_with_match_keyword(
        self,
        mocked_context: BaseFactoryContext,
        test_pytest_bdd_item: Item,
        test_severity: allure.severity_level,
        severity_handler_mock: mock.MagicMock,
    ) -> None:
        set_severity_level(item=test_pytest_bdd_item, keyword=mocked_context.compilation_settings.severity_keyword)
        assert severity_handler_mock.called_once(allure.severity_level)
