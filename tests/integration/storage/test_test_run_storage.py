from typing import Optional

import pytest

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus
from overhave.entities import FeatureModel
from overhave.storage.test_run import TestRunStorage


class TestTestRunStorage:
    """ Integration tests for :class:`TestRunStorage`. """

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_create_test_run(self, test_test_run_id: Optional[int]):
        assert isinstance(test_test_run_id, int)

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
    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_set_run_status(
        self, test_test_run_storage: TestRunStorage, run_status: TestRunStatus, test_test_run_id: Optional[int]
    ):
        test_test_run_storage.set_run_status(test_test_run_id, run_status)
        test_run = test_test_run_storage.get_test_run(test_test_run_id)
        assert test_run.status == run_status

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
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
        test_test_run_storage: TestRunStorage,
        report_status: TestReportStatus,
        test_report: Optional[str],
        test_test_run_id: Optional[int],
    ):
        test_run = test_test_run_storage.get_test_run(test_test_run_id)
        assert test_run.report is None
        test_test_run_storage.set_report(run_id=test_test_run_id, status=report_status, report=test_report)
        test_run = test_test_run_storage.get_test_run(test_test_run_id)
        assert test_run.report_status == report_status
        assert test_run.report == test_report

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_test_run(
        self, test_test_run_storage: TestRunStorage, test_feature: FeatureModel, test_test_run_id: Optional[int]
    ):
        test_run = test_test_run_storage.get_test_run(test_test_run_id)
        assert test_run.id == test_test_run_id
        assert test_run.status == TestRunStatus.STARTED
        assert test_run.executed_by == test_feature.author
        assert test_run.report_status == db.TestReportStatus.EMPTY
