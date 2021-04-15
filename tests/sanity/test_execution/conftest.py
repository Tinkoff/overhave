from typing import Callable, cast
from unittest import mock

import pytest
import werkzeug
from _pytest.fixtures import FixtureRequest

from demo.demo import _run_demo_consumer
from overhave import OverhaveRedisStream
from overhave.db import TestReportStatus
from overhave.entities import ScenarioModel
from overhave.factory import ITestExecutionFactory
from overhave.pytest_plugin import IProxyManager, ProxyManager
from overhave.transport import RedisConsumerRunner, TestRunData, TestRunTask


@pytest.fixture()
def redisconsumer_run_mock() -> mock.MagicMock:
    with mock.patch.object(RedisConsumerRunner, "run", return_value=mock.MagicMock()) as mocked_redisconsumer_run:
        yield mocked_redisconsumer_run


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


@pytest.fixture()
def test_resolved_testexecution_proxy_manager(
    test_resolved_admin_proxy_manager: ProxyManager,
    clean_test_execution_factory: Callable[[], ITestExecutionFactory],
    redisconsumer_run_mock: mock.MagicMock,
    subprocess_run_mock: mock.MagicMock,
) -> IProxyManager:
    test_resolved_admin_proxy_manager._factory = None  # reset ProxyManager factory
    _run_demo_consumer(stream=OverhaveRedisStream.TEST)
    return test_resolved_admin_proxy_manager


@pytest.fixture()
def test_testruntask(test_db_scenario: ScenarioModel) -> TestRunTask:
    return TestRunTask(data=TestRunData(test_run_id=test_db_scenario.id))


@pytest.fixture()
def report_status(request: FixtureRequest) -> TestReportStatus:
    if hasattr(request, "param"):
        return cast(TestReportStatus, request.param)
    raise NotImplementedError


@pytest.fixture()
def test_executed_testruntask_id(
    test_featureview_runtest_result: werkzeug.Response,
    test_resolved_testexecution_proxy_manager: IProxyManager,
    test_testruntask: TestRunTask,
) -> int:
    test_resolved_testexecution_proxy_manager.factory.process_task(test_testruntask)
    return test_testruntask.data.test_run_id
