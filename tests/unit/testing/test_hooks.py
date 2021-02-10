from typing import Type, cast
from unittest import mock

import pytest
from _pytest.config.argparsing import OptionGroup, Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.python import Function
from faker import Faker
from pytest_bdd.parser import Step

from overhave import get_description_manager
from overhave.factory import IOverhaveFactory
from overhave.testing.plugin import (
    _GROUP_HELP,
    _PLUGIN_NAME,
    StepNotFoundError,
    _Options,
    pytest_addoption,
    pytest_bdd_after_step,
    pytest_bdd_apply_tag,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
    pytest_bdd_step_func_lookup_error,
    pytest_runtest_setup,
    pytest_runtest_teardown,
)
from overhave.testing.plugin_utils import StepContextNotDefinedError


@pytest.mark.usefixtures("clear_get_step_context_runner")
class TestPytestBddHooks:
    """ Unit tests for pytest-bdd wrapped hooks. """

    def test_pytest_bdd_before_step(
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_proxy_factory: IOverhaveFactory
    ):
        pytest_bdd_before_step(
            request=request,
            feature=mock.MagicMock(),
            scenario=mock.MagicMock(),
            step=test_pytest_bdd_step,
            step_func=mock.MagicMock(),
        )
        assert cast(mock.MagicMock, patched_proxy_factory.context).called_once()

    def test_pytest_bdd_after_step_failed(
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_proxy_factory: IOverhaveFactory
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
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_proxy_factory: IOverhaveFactory
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
        self, request: FixtureRequest, test_pytest_bdd_step: Step, patched_proxy_factory: IOverhaveFactory
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

    def test_pytest_runtest_setup(self):
        with mock.patch(
            "overhave.get_description_manager", return_value=mock.MagicMock()
        ) as mocked_description_manager:
            pytest_runtest_setup(item=mock.create_autospec(Item))
            mocked_description_manager.assert_not_called()

    def test_pytest_runtest_teardown_description(
        self,
        clear_get_description_manager,
        description_handler_mock: mock.MagicMock,
        faker: Faker,
        patched_proxy_factory: IOverhaveFactory,
    ):
        description_manager = get_description_manager()
        description_manager.add_description(faker.word())
        pytest_runtest_teardown(item=mock.create_autospec(Item))
        description_handler_mock.assert_called_once()


class TestPytestCommonHooks:
    """ Unit tests for pytest wrapped hooks. """

    def test_pytest_addoption(self, test_pytest_parser: Parser):
        pytest_addoption(test_pytest_parser)
        group = test_pytest_parser.getgroup(_PLUGIN_NAME, _GROUP_HELP)
        assert isinstance(group, OptionGroup)
        assert len(group.options) == 2

        assert group.options[0].names() == _Options.enable_injection.names()
        assert group.options[0].attrs() == _Options.enable_injection.attrs()
        assert group.options[1].names() == _Options.context_module.names()
        assert group.options[1].attrs() == _Options.context_module.attrs()
