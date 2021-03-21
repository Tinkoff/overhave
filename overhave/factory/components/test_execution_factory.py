import abc
from functools import cached_property

from overhave.factory import IOverhaveFactory
from overhave.factory.base_factory import BaseOverhaveFactory
from overhave.factory.context import OverhaveTestExecutionContext
from overhave.test_execution import ITestExecutionManager, TestExecutionManager


class ITestExecutionFactory(IOverhaveFactory[OverhaveTestExecutionContext]):
    """ Factory interface for Overhave test execution application. """

    @property
    @abc.abstractmethod
    def test_execution_manager(self) -> ITestExecutionManager:
        pass


class TestExecutionFactory(BaseOverhaveFactory[OverhaveTestExecutionContext], ITestExecutionFactory):
    """ Factory for Overhave test execution application. """

    @cached_property
    def _test_execution_manager(self) -> TestExecutionManager:
        return TestExecutionManager(
            file_settings=self.context.file_settings,
            feature_storage=self._feature_storage,
            scenario_storage=self._scenario_storage,
            test_run_storage=self._test_run_storage,
            file_manager=self._file_manager,
            test_runner=self._test_runner,
            report_manager=self._report_manager,
        )

    @property
    def test_execution_manager(self) -> ITestExecutionManager:
        return self._test_execution_manager
