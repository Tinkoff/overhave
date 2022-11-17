from typing import Any, Callable, Mapping, Optional, Type, cast
from unittest import mock

import allure
import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.python import Function
from faker import Faker
from pytest_bdd.parser import Step

from overhave import get_description_manager
from overhave.factory import ITestExecutionFactory
from overhave.pytest_plugin import IProxyManager, StepContextNotDefinedError, get_feature_info_from_item, get_scenario
from overhave.pytest_plugin.plugin import (
    StepNotFoundError,
    get_step_context_runner,
    pytest_bdd_after_step,
    pytest_bdd_apply_tag,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
    pytest_bdd_step_func_lookup_error,
    pytest_collection_finish,
    pytest_collection_modifyitems,
    pytest_configure,
    pytest_runtest_setup,
    pytest_runtest_teardown,
)
from overhave.scenario import FeatureInfo
from overhave.utils import make_url
from tests.unit.pytest_plugin.getoption_mock import ConfigGetOptionMock


@pytest.mark.usefixtures("clear_get_step_context_runner")
class TestPytestBddHooks:
    """Unit tests for pytest-bdd wrapped hooks."""

    def test_pytest_bdd_before_step(
        self,
        request: FixtureRequest,
        test_pytest_bdd_step: Step,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        pytest_bdd_before_step(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
        )
        assert (
            get_step_context_runner()._settings
            is cast(
                ITestExecutionFactory, patched_hook_test_execution_proxy_manager.factory
            ).context.step_context_settings
        )

    def test_pytest_bdd_after_step_failed(
        self,
        request: FixtureRequest,
        test_pytest_bdd_step: Step,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        with pytest.raises(StepContextNotDefinedError):
            pytest_bdd_after_step(
                request=request,
                feature=mock.MagicMock(),
                scenario=mock.MagicMock(),
                step=test_pytest_bdd_step,
                step_func=mock.MagicMock(),
                step_func_args={},
            )

    def test_pytest_bdd_after_step(
        self,
        request: FixtureRequest,
        test_pytest_bdd_step: Step,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        pytest_bdd_before_step(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
        )
        pytest_bdd_after_step(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
            step_func_args={},
        )

    def test_pytest_bdd_step_error(
        self,
        request: FixtureRequest,
        test_pytest_bdd_step: Step,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        pytest_bdd_before_step(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
        )
        pytest_bdd_step_error(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
            step_func_args={},
            exception=Exception("babah!"),
        )

    def test_pytest_bdd_apply_tag_not_suitable(self, test_pytest_function: Function, faker: Faker) -> None:
        assert pytest_bdd_apply_tag(tag=faker.word(), function=test_pytest_function) is None

    @pytest.mark.parametrize("tag", ["disabled(kek)", "xfail(lol)"])
    def test_pytest_bdd_apply_tag_without_url(
        self, link_handler_mock: mock.MagicMock, test_pytest_function: Function, tag: str
    ) -> None:
        assert pytest_bdd_apply_tag(tag=tag, function=test_pytest_function) is True
        link_handler_mock.assert_not_called()

    @pytest.mark.parametrize(
        "tag",
        [
            "disabled(TODO: https://link/to/disabling/reason; deadline: 01.01.99)",
            "xfail(wait until bug https://link/to/bug will be fixed)",
        ],
    )
    def test_pytest_bdd_apply_tag_with_url(
        self, link_handler_mock: mock.MagicMock, test_pytest_function: Function, tag: str
    ) -> None:
        assert pytest_bdd_apply_tag(tag=tag, function=test_pytest_function) is True
        link_handler_mock.assert_called_once()

    @pytest.mark.parametrize("exception", [Exception])
    def test_pytest_bdd_step_func_lookup_error(
        self, request: FixtureRequest, test_pytest_bdd_step: Step, exception: Type[BaseException]
    ) -> None:
        with pytest.raises(StepNotFoundError):
            pytest_bdd_step_func_lookup_error(
                request=request,
                feature=mock.MagicMock(),
                scenario=mock.MagicMock(),
                step=test_pytest_bdd_step,
                exception=exception("babah!"),
            )


class TestPytestCommonHooks:
    """Unit tests for pytest wrapped hooks."""

    def test_pytest_configure_disabled(
        self,
        terminal_writer_mock: mock.MagicMock,
        test_prepared_config: Config,
        clean_proxy_manager: Callable[[], IProxyManager],
    ) -> None:
        pytest_configure(test_prepared_config)
        terminal_writer_mock.assert_not_called()
        assert not clean_proxy_manager().pytest_patched

    def test_pytest_configure_enabled_injection(
        self,
        terminal_writer_mock: mock.MagicMock,
        test_prepared_config: Config,
        getoption_mapping: Mapping[str, Any],
        getoption_mock: ConfigGetOptionMock,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        pytest_configure(test_prepared_config)
        terminal_writer_mock.assert_called_once()
        assert patched_hook_test_execution_proxy_manager.pytest_patched

    def test_pytest_collection_modifyitems_clean(
        self,
        test_clean_item: Item,
        test_pytest_clean_session: Session,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        with mock.patch(
            "overhave.pytest_plugin.helpers.bdd_item.add_scenario_title_to_report",
            return_value=mock.MagicMock(),
        ) as mocked_title_func:
            pytest_collection_modifyitems(test_pytest_clean_session)
            mocked_title_func.assert_not_called()

    @pytest.mark.parametrize(
        ("task_tracker_url", "tasks_keyword"),
        [(None, None), ("https://tasktracker.mydomain.com/browse", "Tasks")],
    )
    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_pytest_collection_modifyitems_bdd(
        self,
        test_pytest_bdd_item: Item,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager: IProxyManager,
        tasks_keyword: Optional[str],
    ) -> None:
        patched_hook_test_execution_proxy_manager.factory.context.project_settings.tasks_keyword = tasks_keyword
        pytest_collection_modifyitems(test_pytest_bdd_session)
        assert (
            test_pytest_bdd_item._obj.__allure_display_name__ == get_scenario(test_pytest_bdd_item).name  # type: ignore
        )

    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_pytest_collection_finish_injection_disabled(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
    ) -> None:
        pytest_collection_finish(test_pytest_bdd_session)
        terminal_writer_mock.assert_not_called()

    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_pytest_collection_finish_admin_factory_injection_enabled_with_not_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_admin_proxy_manager: IProxyManager,
    ) -> None:
        pytest_collection_finish(test_pytest_bdd_session)
        terminal_writer_mock.assert_called_once()
        assert not patched_hook_admin_proxy_manager.collection_prepared

    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_pytest_collection_finish_test_execution_factory_injection_enabled_with_not_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        pytest_collection_finish(test_pytest_bdd_session)
        terminal_writer_mock.assert_not_called()
        assert not patched_hook_test_execution_proxy_manager.collection_prepared

    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_pytest_collection_admin_factory_finish_injection_enabled_with_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_admin_proxy_manager: IProxyManager,
    ) -> None:
        pytest_configure(test_pytest_bdd_session.config)
        pytest_collection_finish(test_pytest_bdd_session)
        assert terminal_writer_mock.call_count == 2
        assert patched_hook_admin_proxy_manager.collection_prepared

    @pytest.mark.parametrize("test_severity", [None], indirect=True)
    def test_pytest_collection_finish_test_execution_factory_injection_enabled_with_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        pytest_configure(test_pytest_bdd_session.config)
        pytest_collection_finish(test_pytest_bdd_session)
        assert terminal_writer_mock.call_count == 1
        assert not patched_hook_test_execution_proxy_manager.collection_prepared

    def test_pytest_runtest_setup_clean(
        self,
        test_clean_item: Item,
        severity_handler_mock: mock.MagicMock,
        link_handler_mock: mock.MagicMock,
    ) -> None:
        with mock.patch(
            "overhave.get_description_manager", return_value=mock.MagicMock()
        ) as mocked_description_manager:
            pytest_runtest_setup(item=test_clean_item)
            mocked_description_manager.assert_not_called()
            link_handler_mock.assert_not_called()
            severity_handler_mock.assert_not_called()
            with pytest.raises(AttributeError):
                get_feature_info_from_item(test_clean_item)

    @pytest.mark.parametrize(
        ("task_tracker_url", "tasks_keyword"),
        [(None, None), ("https://tasktracker.mydomain.com/browse", "Tasks")],
    )
    @pytest.mark.parametrize("admin_url", [None, "https://overhave.mydomain.com"])
    @pytest.mark.parametrize("test_severity", list(allure.severity_level), indirect=True)
    @pytest.mark.parametrize("git_project_url", [None, "https://overhave.mydomain.com/bdd-features"], indirect=True)
    def test_pytest_runtest_setup_pytest_bdd(
        self,
        test_pytest_bdd_item: Item,
        test_pytest_bdd_session: Session,
        severity_handler_mock: mock.MagicMock,
        test_severity: allure.severity_level,
        link_handler_mock: mock.MagicMock,
        patched_hook_test_execution_proxy_manager: IProxyManager,
        task_tracker_url: Optional[str],
        tasks_keyword: Optional[str],
        admin_url: Optional[str],
        git_project_url: Optional[str],
        faker: Faker,
    ) -> None:
        with mock.patch(
            "overhave.get_description_manager", return_value=mock.MagicMock()
        ) as mocked_description_manager:
            patched_hook_test_execution_proxy_manager.factory.context.project_settings.task_tracker_url = make_url(
                task_tracker_url
            )
            patched_hook_test_execution_proxy_manager.factory.context.project_settings.tasks_keyword = tasks_keyword

            pytest_collection_modifyitems(test_pytest_bdd_session)
            pytest_runtest_setup(item=test_pytest_bdd_item)
            mocked_description_manager.assert_not_called()

            assert isinstance(get_feature_info_from_item(test_pytest_bdd_item), FeatureInfo)

            link_handler_mock_calls = 0
            if task_tracker_url is not None:
                link_handler_mock_calls += 2
            if git_project_url is not None:
                link_handler_mock_calls += 1
            assert link_handler_mock.call_count == link_handler_mock_calls

            severity_handler_mock.assert_called_once_with(test_severity)

    @pytest.mark.parametrize("enable_html", [True])
    def test_pytest_runtest_teardown_clean(
        self,
        clear_get_description_manager: None,
        description_handler_mock: mock.MagicMock,
        faker: Faker,
        test_clean_item: Item,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ) -> None:
        description_manager = get_description_manager()
        description_manager.add_description(faker.word())
        pytest_runtest_teardown(item=test_clean_item, nextitem=None)
        description_handler_mock.assert_called_once()
