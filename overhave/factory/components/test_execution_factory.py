import abc
from functools import cached_property

from overhave.factory.base_factory import IOverhaveFactory
from overhave.factory.components.abstract_consumer import ITaskConsumerFactory
from overhave.factory.components.s3_init_factory import FactoryWithS3ManagerInit
from overhave.factory.context import OverhaveTestExecutionContext
from overhave.test_execution.executor import ITestExecutor, TestExecutor
from overhave.transport import TestRunTask


class ITestExecutionFactory(IOverhaveFactory[OverhaveTestExecutionContext], ITaskConsumerFactory[TestRunTask], abc.ABC):
    """Abstract factory for Overhave test execution application."""

    @property
    @abc.abstractmethod
    def test_executor(self) -> ITestExecutor:
        pass


class TestExecutionFactory(FactoryWithS3ManagerInit[OverhaveTestExecutionContext], ITestExecutionFactory):
    """Factory for Overhave test execution application."""

    context_cls = OverhaveTestExecutionContext

    @cached_property
    def _test_executor(self) -> ITestExecutor:
        return TestExecutor(
            file_settings=self.context.file_settings,
            feature_storage=self._feature_storage,
            scenario_storage=self._scenario_storage,
            test_run_storage=self._test_run_storage,
            file_manager=self._file_manager,
            test_runner=self._test_runner,
            report_manager=self._report_manager,
        )

    @property
    def test_executor(self) -> ITestExecutor:
        return self._test_executor

    def process_task(self, task: TestRunTask) -> None:
        return self._test_executor.process_test_task(task)
