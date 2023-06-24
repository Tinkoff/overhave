import abc
import logging
import tempfile
from pathlib import Path

from overhave import db
from overhave.db import TestRunStatus
from overhave.entities import OverhaveFileSettings, ReportManager
from overhave.metrics import TestRunOverhaveMetricContainer
from overhave.scenario import FileManager
from overhave.storage import IFeatureStorage, IScenarioStorage, ITestRunStorage, TestExecutorContext
from overhave.test_execution.test_runner import PytestRunner
from overhave.transport import TestRunTask

logger = logging.getLogger(__name__)


class ITestExecutor(abc.ABC):
    """Abstract class for test execution."""

    @abc.abstractmethod
    def execute_test(self, test_run_id: int) -> None:
        pass

    @abc.abstractmethod
    def process_test_task(self, task: TestRunTask) -> None:
        pass


class TestExecutor(ITestExecutor):
    """Class for test execution."""

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        test_run_storage: ITestRunStorage,
        file_manager: FileManager,
        test_runner: PytestRunner,
        report_manager: ReportManager,
        metric_container: TestRunOverhaveMetricContainer,
    ):
        self._file_settings = file_settings
        self._feature_storage = feature_storage
        self._scenario_storage = scenario_storage
        self._test_run_storage = test_run_storage
        self._file_manager = file_manager
        self._test_runner = test_runner
        self._report_manager = report_manager
        self._metric_container = metric_container

    def _run_test(self, context: TestExecutorContext, alluredir: Path) -> int:
        with self._file_manager.tmp_feature_file(context=context) as feature_file:
            with self._file_manager.tmp_fixture_file(context=context, feature_file=feature_file) as fixture_file:
                return self._test_runner.run(fixture_file=fixture_file.name, alluredir=alluredir.as_posix())

    def _compile_context(self, test_run_id: int) -> TestExecutorContext:
        with db.create_session() as session:
            test_run_model = self._test_run_storage.testrun_model_by_id(session=session, run_id=test_run_id)
            scenario_model = self._scenario_storage.scenario_model_by_id(
                session=session, scenario_id=test_run_model.scenario_id
            )
            feature_model = self._feature_storage.feature_model_by_id(
                session=session, feature_id=scenario_model.feature_id
            )
        return TestExecutorContext(
            feature=feature_model,
            scenario=scenario_model,
            test_run=test_run_model,
        )

    def execute_test(self, test_run_id: int) -> None:
        self._test_run_storage.set_run_status(run_id=test_run_id, status=TestRunStatus.RUNNING)
        ctx = self._compile_context(test_run_id)

        results_dir = Path(tempfile.mkdtemp())
        logger.debug("Allure results directory path: %s", results_dir.as_posix())
        try:
            test_return_code = self._run_test(context=ctx, alluredir=results_dir)
        except Exception as e:
            logger.exception("Error!")
            self._test_run_storage.set_run_status(
                run_id=test_run_id, status=TestRunStatus.INTERNAL_ERROR, traceback=str(e)
            )
            self._metric_container.add_test_run_status(status=TestRunStatus.INTERNAL_ERROR.value)
            return

        logger.debug("Test returncode: %s", test_return_code)
        if test_return_code == 0:
            self._test_run_storage.set_run_status(run_id=test_run_id, status=TestRunStatus.SUCCESS)
            self._metric_container.add_test_run_status(status=TestRunStatus.SUCCESS.value)
        else:
            self._test_run_storage.set_run_status(
                run_id=test_run_id, status=TestRunStatus.FAILED, traceback="Test run failed!"
            )
            self._metric_container.add_test_run_status(status=TestRunStatus.FAILED.value)
        self._report_manager.create_allure_report(test_run_id=test_run_id, results_dir=results_dir)

    def process_test_task(self, task: TestRunTask) -> None:
        self.execute_test(test_run_id=task.data.test_run_id)
