from typing import Callable, cast
from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest

from overhave.factory import ITestExecutionFactory


@pytest.fixture()
def test_testexecution_factory(
    clean_test_execution_factory: Callable[[], ITestExecutionFactory]
) -> ITestExecutionFactory:
    return clean_test_execution_factory()


@pytest.fixture()
def run_test_process_result(request: FixtureRequest) -> int:
    if hasattr(request, "param"):
        return cast(int, request.param)
    raise NotImplementedError


@pytest.fixture()
def subprocess_run_mock(run_test_process_result: int) -> mock.MagicMock:
    returncode_mock = mock.MagicMock()
    returncode_mock.returncode = run_test_process_result
    with mock.patch("subprocess.run", return_value=returncode_mock) as mocked_subprocess_run:
        yield mocked_subprocess_run
