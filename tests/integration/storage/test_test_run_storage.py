import pytest
from faker import Faker

from overhave import db
from overhave.db import TestReportStatus, TestRunStatus
from overhave.entities import ScenarioModel
from overhave.storage.test_run import TestRunStorage


class TestTestRunStorage:
    """ Integration tests for :class:`TestRunStorage`. """

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_create_test_run(
        self,
        test_test_run_storage: TestRunStorage,
        test_scenario: ScenarioModel,
        faker: Faker,
    ):
        feature = test_test_run_storage._get_feature_by_id(test_scenario.feature_id)
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, feature.author)
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
    ):
        feature = test_test_run_storage._get_feature_by_id(test_scenario.feature_id)
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, feature.author)
        test_test_run_storage.set_run_status(test_run_id, run_status)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.status == run_status

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    @pytest.mark.parametrize(
        "report_status",
        [
            TestReportStatus.GENERATED,
            TestReportStatus.GENERATION_FAILED,
            TestReportStatus.SAVED,
            TestReportStatus.EMPTY,
        ],
    )
    def test_set_report(
        self,
        test_test_run_storage: TestRunStorage,
        test_scenario: ScenarioModel,
        report_status: TestReportStatus,
    ):
        feature = test_test_run_storage._get_feature_by_id(test_scenario.feature_id)
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, feature.author)
        test_test_run_storage.set_report(test_run_id, report_status)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.report_status == report_status

    @pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
    def test_get_test_run(self, test_test_run_storage: TestRunStorage, test_scenario: ScenarioModel):
        feature = test_test_run_storage._get_feature_by_id(test_scenario.feature_id)
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, feature.author)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.id == test_run_id
        assert test_run.status == TestRunStatus.STARTED
        assert test_run.executed_by == feature.author
        assert test_run.report_status == db.TestReportStatus.EMPTY
