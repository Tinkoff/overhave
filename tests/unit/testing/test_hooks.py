from typing import Any, Mapping, Optional, Type, cast
from unittest import mock

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import OptionGroup, Parser
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.python import Function
from faker import Faker
from pytest_bdd.parser import Step

from overhave import get_description_manager
from overhave.pytest_plugin import IProxyManager, StepContextNotDefinedError, get_scenario, has_issue_links
from overhave.pytest_plugin.plugin import (
    _GROUP_HELP,
    _PLUGIN_NAME,
    StepNotFoundError,
    _OptionName,
    _Options,
    pytest_addoption,
    pytest_bdd_after_step,
    pytest_bdd_apply_tag,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
    pytest_bdd_step_func_lookup_error,
    pytest_collection_finish,
    pytest_collection_modifyitems,
    pytest_configure,
    pytest_runtest_makereport,
    pytest_runtest_setup,
)
from tests.unit.testing.getoption_mock import ConfigGetOptionMock


@pytest.mark.usefixtures("clear_get_step_context_runner")
class TestPytestBddHooks:
    """ Unit tests for pytest-bdd wrapped hooks. """

    def test_pytest_bdd_before_step(
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_hook_test_execution_proxy_manager
    ):
        pytest_bdd_before_step(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
        )
        assert cast(mock.MagicMock, patched_hook_test_execution_proxy_manager.factory.context).called_once()

    def test_pytest_bdd_after_step_failed(
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_hook_test_execution_proxy_manager
    ):
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
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_hook_test_execution_proxy_manager
    ):
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
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_hook_test_execution_proxy_manager
    ):
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

    @pytest.mark.parametrize("tag", ["random"])
    def test_pytest_bdd_apply_tag_not_skip(self, test_pytest_function: Function, tag: str):
        assert pytest_bdd_apply_tag(tag=tag, function=test_pytest_function) is None

    @pytest.mark.parametrize("tag", ["skip"])
    def test_pytest_bdd_apply_tag_skip(self, test_pytest_function: Function, tag: str):
        assert pytest_bdd_apply_tag(tag=tag, function=test_pytest_function) is True

    @pytest.mark.parametrize("exception", [Exception])
    def test_pytest_bdd_step_func_lookup_error(
        self, request: FixtureRequest, test_pytest_bdd_step: Step, exception: Type[BaseException]
    ):
        with pytest.raises(StepNotFoundError):
            pytest_bdd_step_func_lookup_error(
                request=request,
                feature=mock.MagicMock(),
                scenario=mock.MagicMock(),
                step=test_pytest_bdd_step,
                exception=exception("babah!"),
            )


class TestPytestCommonHooks:
    """ Unit tests for pytest wrapped hooks. """

    def test_pytest_addoption(self, test_pytest_parser: Parser):
        pytest_addoption(test_pytest_parser)
        group = test_pytest_parser.getgroup(_PLUGIN_NAME, _GROUP_HELP)
        assert isinstance(group, OptionGroup)
        assert len(group.options) == 1

        assert group.options[0].names() == _Options.enable_injection.names()
        assert group.options[0].attrs() == _Options.enable_injection.attrs()

    def test_pytest_configure_failed_no_option(self, test_empty_config: Config):
        with pytest.raises(ValueError, match="no option named"):
            pytest_configure(test_empty_config)

    def test_pytest_configure_disabled_options(
        self,
        terminal_writer_mock: mock.MagicMock,
        test_prepared_config: Config,
        patched_hook_test_execution_proxy_manager,
    ):
        pytest_configure(test_prepared_config)
        assert test_prepared_config.getoption(_OptionName.ENABLE_INJECTION.as_variable) is False
        terminal_writer_mock.assert_called_once()
        assert not patched_hook_test_execution_proxy_manager.pytest_patched

    @pytest.mark.parametrize("getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: True}], indirect=True)
    def test_pytest_configure_enabled_injection(
        self,
        test_prepared_config: Config,
        getoption_mapping: Mapping[str, Any],
        getoption_mock: ConfigGetOptionMock,
        patched_hook_test_execution_proxy_manager,
    ):
        assert test_prepared_config.getoption(_OptionName.ENABLE_INJECTION.as_variable) is getoption_mapping.get(
            _OptionName.ENABLE_INJECTION.as_variable
        )
        pytest_configure(test_prepared_config)
        assert patched_hook_test_execution_proxy_manager.pytest_patched

    @pytest.mark.parametrize(
        "getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: False}], indirect=True,
    )
    def test_pytest_configure_disabled_injection(
        self,
        test_prepared_config: Config,
        getoption_mapping: Mapping[str, Any],
        getoption_mock: ConfigGetOptionMock,
        patched_hook_test_execution_proxy_manager,
    ):
        assert test_prepared_config.getoption(_OptionName.ENABLE_INJECTION.as_variable) is getoption_mapping.get(
            _OptionName.ENABLE_INJECTION.as_variable
        )
        pytest_configure(test_prepared_config)
        assert not patched_hook_test_execution_proxy_manager.pytest_patched

    def test_pytest_collection_modifyitems_clean(self, test_clean_item: Item, test_pytest_clean_session: Session):
        with mock.patch(
            "overhave.pytest_plugin.helpers.allure_utils.common.add_scenario_title_to_report",
            return_value=mock.MagicMock(),
        ) as mocked_title_func:
            pytest_collection_modifyitems(test_pytest_clean_session)
            mocked_title_func.assert_not_called()

    @pytest.mark.parametrize("links_keyword", [None, "Tasks"])
    def test_pytest_collection_modifyitems_bdd(
        self,
        test_pytest_bdd_item: Item,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager,
        links_keyword: Optional[str],
    ):
        patched_hook_test_execution_proxy_manager.factory.context.project_settings.links_keyword = links_keyword
        pytest_collection_modifyitems(test_pytest_bdd_session)
        assert test_pytest_bdd_item._obj.__allure_display_name__ == get_scenario(test_pytest_bdd_item).name

        if links_keyword is None:
            assert not has_issue_links(test_pytest_bdd_item)
        else:
            assert has_issue_links(test_pytest_bdd_item)

    @pytest.mark.parametrize("getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: False}], indirect=True)
    def test_pytest_collection_finish_injection_disabled(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
    ):
        pytest_collection_finish(test_pytest_bdd_session)
        terminal_writer_mock.assert_not_called()

    @pytest.mark.parametrize("getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: True}], indirect=True)
    def test_pytest_collection_finish_admin_factory_injection_enabled_with_not_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_admin_proxy_manager: IProxyManager,
    ):
        pytest_collection_finish(test_pytest_bdd_session)
        terminal_writer_mock.assert_called_once()
        assert not patched_hook_admin_proxy_manager.collection_prepared

    @pytest.mark.parametrize("getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: True}], indirect=True)
    def test_pytest_collection_finish_test_execution_factory_injection_enabled_with_not_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager: IProxyManager,
    ):
        pytest_collection_finish(test_pytest_bdd_session)
        terminal_writer_mock.assert_not_called()
        assert not patched_hook_test_execution_proxy_manager.collection_prepared

    @pytest.mark.parametrize("getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: True}], indirect=True)
    def test_pytest_collection_admin_factory_finish_injection_enabled_with_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_admin_proxy_manager,
    ):
        pytest_configure(test_pytest_bdd_session.config)
        pytest_collection_finish(test_pytest_bdd_session)
        assert terminal_writer_mock.call_count == 2
        assert patched_hook_admin_proxy_manager.collection_prepared

    @pytest.mark.parametrize("getoption_mapping", [{_OptionName.ENABLE_INJECTION.as_variable: True}], indirect=True)
    def test_pytest_collection_finish_test_execution_factory_injection_enabled_with_patched_pytest(
        self,
        terminal_writer_mock: mock.MagicMock,
        getoption_mock: ConfigGetOptionMock,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager,
    ):
        pytest_configure(test_pytest_bdd_session.config)
        pytest_collection_finish(test_pytest_bdd_session)
        assert terminal_writer_mock.call_count == 1
        assert not patched_hook_test_execution_proxy_manager.collection_prepared

    def test_pytest_runtest_setup(self, test_clean_item: Item):
        with mock.patch(
            "overhave.get_description_manager", return_value=mock.MagicMock()
        ) as mocked_description_manager:
            pytest_runtest_setup(item=test_clean_item)
            mocked_description_manager.assert_not_called()

    def test_pytest_runtest_makereport_clean(
        self,
        clear_get_description_manager,
        description_handler_mock: mock.MagicMock,
        link_handler_mock: mock.MagicMock,
        faker: Faker,
        test_clean_item: Item,
        patched_hook_test_execution_proxy_manager,
    ):
        description_manager = get_description_manager()
        description_manager.add_description(faker.word())
        pytest_runtest_makereport(item=test_clean_item, call=mock.MagicMock())
        description_handler_mock.assert_called_once()
        link_handler_mock.assert_not_called()

    @pytest.mark.parametrize(
        ("browse_url", "links_keyword"), [(None, None), ("https://overhave.readthedocs.io/browse", "Tasks")]
    )
    def test_pytest_runtest_makereport_bdd(
        self,
        clear_get_description_manager,
        description_handler_mock: mock.MagicMock,
        link_handler_mock: mock.MagicMock,
        faker: Faker,
        test_pytest_bdd_item: Item,
        test_pytest_bdd_session: Session,
        patched_hook_test_execution_proxy_manager,
        browse_url: Optional[str],
        links_keyword: Optional[str],
    ):
        description_manager = get_description_manager()
        description_manager.add_description(faker.word())

        patched_hook_test_execution_proxy_manager.factory.context.project_settings.browse_url = browse_url
        patched_hook_test_execution_proxy_manager.factory.context.project_settings.links_keyword = links_keyword

        pytest_collection_modifyitems(test_pytest_bdd_session)
        pytest_runtest_makereport(item=test_pytest_bdd_item, call=mock.MagicMock())
        description_handler_mock.assert_called_once()

        if browse_url is None:
            link_handler_mock.assert_not_called()
        else:
            assert has_issue_links(test_pytest_bdd_item)
            assert link_handler_mock.call_count == 2  # 2 tags in test_pytest_bdd_item feature
