from typing import Optional
from uuid import uuid1

import pytest

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus
from overhave.entities import FeatureModel, ScenarioModel
from overhave.storage.test_run import TestRunStorage


class TestTestRunStorage:
    """ Integration tests for :class:`TestRunStorage`. """

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_create_test_run(
        self,
        test_test_run_storage: TestRunStorage,
        test_scenario: ScenarioModel,
        test_feature: FeatureModel,
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_feature.author)
        assert isinstance(test_run_id, int)

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
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
        self,
        test_test_run_storage: TestRunStorage,
        test_scenario: ScenarioModel,
        run_status: TestRunStatus,
        test_feature: FeatureModel,
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_feature.author)
        test_test_run_storage.set_run_status(test_run_id, run_status)
        test_run = test_test_run_storage.get_test_run(test_run_id)
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
    @pytest.mark.parametrize("report", [uuid1().hex])
    def test_set_report(
        self,
        test_test_run_storage: TestRunStorage,
        test_scenario: ScenarioModel,
        report_status: TestReportStatus,
        test_feature: FeatureModel,
        report: Optional[str],
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_feature.author)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.report is None
        test_test_run_storage.set_report(run_id=test_run_id, status=report_status, report=report)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.report_status == report_status
        assert test_run.report is report

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_test_run(
        self, test_test_run_storage: TestRunStorage, test_feature: FeatureModel, test_scenario: ScenarioModel
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_feature.author)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.id == test_run_id
        assert test_run.status == TestRunStatus.STARTED
        assert test_run.executed_by == test_feature.author
        assert test_run.report_status == db.TestReportStatus.EMPTY
