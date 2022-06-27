from typing import Optional
from unittest import mock

import allure
import allure_commons.types
import pytest
from _pytest.nodes import Item
from faker import Faker
from pytest_bdd.parser import Scenario, Step

from overhave.factory.context.base_context import BaseFactoryContext
from overhave.pytest_plugin import IProxyManager, get_scenario
from overhave.pytest_plugin.helpers import (
    add_admin_feature_link_to_report,
    add_scenario_title_to_report,
    add_task_links_to_report,
    get_feature_info_from_item,
    get_full_step_name,
    is_pytest_bdd_item,
    set_feature_info_for_item,
    set_severity_level,
)
from overhave.test_execution.settings import EmptyTaskTrackerURLError, OverhaveProjectSettings


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

    @pytest.mark.parametrize("tasks_keyword", ["Tasks"])
    @pytest.mark.parametrize("test_task_tracker_url", ["https://overhave.readthedocs.io/"], indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_add_issue_links_to_report_with_correct_tracker_url(
        self,
        test_pytest_bdd_item: Item,
        test_task_tracker_url: Optional[str],
        test_project_settings: OverhaveProjectSettings,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        set_feature_info_for_item(
            item=test_pytest_bdd_item, scenario_parser=patched_hook_test_execution_proxy_manager.factory.scenario_parser
        )
        feature_info = get_feature_info_from_item(test_pytest_bdd_item)
        assert feature_info.tasks
        add_task_links_to_report(project_settings=test_project_settings, tasks=feature_info.tasks)

    @pytest.mark.parametrize("test_task_tracker_url", [None], indirect=True)
    def test_add_issue_links_to_report_with_empty_tracker_url(
        self,
        test_task_tracker_url: Optional[str],
        test_project_settings: OverhaveProjectSettings,
    ) -> None:
        with pytest.raises(EmptyTaskTrackerURLError):
            add_task_links_to_report(project_settings=test_project_settings, tasks=["PRJ-321"])

    @pytest.mark.parametrize("admin_url", ["https://overhave.mydomain.com"], indirect=True)
    def test_add_admin_feature_link_succeed(
        self,
        patched_hook_test_execution_proxy_manager: IProxyManager,
        link_handler_mock: mock.MagicMock,
        faker: Faker,
    ) -> None:
        settings = patched_hook_test_execution_proxy_manager.factory.context.admin_link_settings  # type: ignore
        feature_id = faker.random_int()
        add_admin_feature_link_to_report(admin_link_settings=settings, feature_id=feature_id)
        link_handler_mock.assert_called_once_with(
            url=settings.get_feature_url(feature_id),
            link_type=allure_commons.types.LinkType.TEST_CASE,
            name=settings.get_feature_link_name(feature_id),
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
    @pytest.mark.parametrize("severity_prefix", ["yet_another_prefix"])
    def test_set_severity_not_match_keyword(
        self,
        mocked_context: BaseFactoryContext,
        test_pytest_bdd_item: Item,
        severity_handler_mock: mock.MagicMock,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        set_feature_info_for_item(
            item=test_pytest_bdd_item, scenario_parser=patched_hook_test_execution_proxy_manager.factory.scenario_parser
        )
        set_severity_level(item=test_pytest_bdd_item, compilation_settings=mocked_context.compilation_settings)
        severity_handler_mock.assert_called_once_with(allure.severity_level.NORMAL)

    @pytest.mark.parametrize("test_severity", list(allure.severity_level), indirect=True)
    def test_set_severity_with_match_keyword_by_tag(
        self,
        mocked_context: BaseFactoryContext,
        test_pytest_bdd_item: Item,
        test_severity: allure.severity_level,
        severity_handler_mock: mock.MagicMock,
    ) -> None:
        set_severity_level(item=test_pytest_bdd_item, compilation_settings=mocked_context.compilation_settings)
        severity_handler_mock.assert_called_once_with(test_severity)

    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_set_severity_with_match_keyword_by_feature(
        self,
        mocked_context: BaseFactoryContext,
        test_pytest_bdd_item: Item,
        test_severity: Optional[allure.severity_level],
        severity_handler_mock: mock.MagicMock,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        set_feature_info_for_item(
            item=test_pytest_bdd_item, scenario_parser=patched_hook_test_execution_proxy_manager.factory.scenario_parser
        )
        set_severity_level(item=test_pytest_bdd_item, compilation_settings=mocked_context.compilation_settings)
        severity_handler_mock.assert_called_once_with(allure.severity_level.CRITICAL)
