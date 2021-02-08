from typing import Type, cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.python import Function
from pytest_bdd.parser import Step

from overhave.factory import IOverhaveFactory
from overhave.testing.plugin import (
    StepNotFoundError,
    pytest_bdd_after_step,
    pytest_bdd_apply_tag,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
    pytest_bdd_step_func_lookup_error,
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
