from functools import cached_property

from overhave.factory.base_factory import BaseOverhaveFactory
from overhave.factory.components.abstract_consumer import ITaskConsumerFactory
from overhave.factory.context import OverhaveTestExecutionContext
from overhave.test_execution import ITestExecutionManager, TestExecutionManager
from overhave.transport import TestRunTask


class TestExecutionFactory(BaseOverhaveFactory[OverhaveTestExecutionContext], ITaskConsumerFactory[TestRunTask]):
    """ Factory for Overhave test execution application. """

    context_cls = OverhaveTestExecutionContext

    @cached_property
    def _test_execution_manager(self) -> ITestExecutionManager:
        return TestExecutionManager(
            file_settings=self.context.file_settings,
            feature_storage=self._feature_storage,
            scenario_storage=self._scenario_storage,
            test_run_storage=self._test_run_storage,
            file_manager=self._file_manager,
            test_runner=self._test_runner,
            report_manager=self._report_manager,
        )

    def process_task(self, task: TestRunTask) -> None:
        return self._test_execution_manager.execute_test(task)
