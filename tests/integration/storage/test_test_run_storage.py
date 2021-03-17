import pytest
from faker import Faker

from overhave import db
from overhave.db import TestRunStatus, TestReportStatus
from overhave.entities import ScenarioModel, SystemUserModel
from overhave.storage.test_run import TestRunStorage


class TestTestRunStorage:
    """ Integration tests for :class:`TestRunStorage`. """

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_create_test_run(
        self,
        test_test_run_storage: TestRunStorage,
        test_system_user: SystemUserModel,
        test_scenario: ScenarioModel,
        faker: Faker,
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_system_user.login)
        assert isinstance(test_run_id, int)

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
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
        test_system_user: SystemUserModel,
        test_scenario: ScenarioModel,
        run_status: TestRunStatus,
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_system_user.login)
        test_test_run_storage.set_run_status(test_run_id, run_status)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.status == run_status

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
        test_system_user: SystemUserModel,
        test_scenario: ScenarioModel,
        report_status: TestReportStatus,
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_system_user.login)
        test_test_run_storage.set_report(test_run_id, report_status)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.report_status == report_status

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_get_test_run(
        self, test_test_run_storage: TestRunStorage, test_system_user: SystemUserModel, test_scenario: ScenarioModel
    ):
        test_run_id = test_test_run_storage.create_test_run(test_scenario.id, test_system_user.login)
        test_run = test_test_run_storage.get_test_run(test_run_id)
        assert test_run.id == test_run_id
        assert test_run.status == TestRunStatus.STARTED
        assert test_run.executed_by == test_system_user.login
        assert test_run.report_status == db.TestReportStatus.EMPTY
