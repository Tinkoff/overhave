import allure
import pytest

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus
from overhave.storage import FeatureModel, ScenarioModel, TestRunModel, TestRunStorage
from tests.db_utils import count_queries


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
@pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
class TestTestRunStorage:
    """Integration tests for :class:`TestRunStorage`."""

    def test_create_test_run(
        self, test_run_storage: TestRunStorage, test_scenario: ScenarioModel, test_feature: FeatureModel
    ) -> None:
        with count_queries(3):
            test_run = test_run_storage.create_test_run(test_scenario.id, test_feature.author)
        assert isinstance(test_run, int)

    @pytest.mark.parametrize(
        "run_status",
        [
            TestRunStatus.RUNNING,
            TestRunStatus.FAILED,
            TestRunStatus.STARTED,
            TestRunStatus.SUCCESS,
            TestRunStatus.INTERNAL_ERROR,
        ],
    )
    def test_set_run_status(
        self, test_run_storage: TestRunStorage, run_status: TestRunStatus, test_created_test_run_id: int
    ) -> None:
        with count_queries(1):
            test_run_storage.set_run_status(test_created_test_run_id, run_status)
        with count_queries(1):
            test_run = test_run_storage.get_test_run(test_created_test_run_id)
        assert isinstance(test_run, TestRunModel)
        assert test_run.status == run_status

    @pytest.mark.parametrize(
        "report_status",
        [
            TestReportStatus.GENERATED,
            TestReportStatus.GENERATION_FAILED,
            TestReportStatus.EMPTY,
            TestReportStatus.SAVED,
        ],
    )
    def test_set_report(
        self,
        test_run_storage: TestRunStorage,
        report_status: TestReportStatus,
        test_report: str | None,
        test_created_test_run_id: int,
    ) -> None:
        with count_queries(1):
            test_run = test_run_storage.get_test_run(test_created_test_run_id)
        assert isinstance(test_run, TestRunModel)
        with count_queries(1):
            test_run_storage.set_report(run_id=test_created_test_run_id, status=report_status, report=test_report)
        with count_queries(1):
            updated_test_run = test_run_storage.get_test_run(test_created_test_run_id)
        assert isinstance(updated_test_run, TestRunModel)
        assert updated_test_run.report_status == report_status
        assert updated_test_run.report == test_report

    def test_get_test_run(
        self, test_run_storage: TestRunStorage, test_feature: FeatureModel, test_created_test_run_id: int
    ) -> None:
        with count_queries(1):
            test_run = test_run_storage.get_test_run(test_created_test_run_id)
        assert isinstance(test_run, TestRunModel)
        assert test_run.id == test_created_test_run_id
        assert test_run.status == TestRunStatus.STARTED
        assert test_run.executed_by == test_feature.author
        assert test_run.report_status == db.TestReportStatus.EMPTY
