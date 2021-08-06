from datetime import datetime
from unittest import mock

import pytest
import werkzeug

from demo.settings import OverhaveDemoAppLanguage
from overhave import db
from overhave.admin.views.feature import _SCENARIO_PREFIX
from overhave.entities import ScenarioModel, SystemUserModel, TestRunModel
from overhave.transport import TestRunData, TestRunTask
from tests.objects import FeatureTestContainer


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_demo_language", list(OverhaveDemoAppLanguage), indirect=True)
class TestOverhaveAdminRunTest:
    """ Sanity tests for application test run. """

    @pytest.mark.parametrize(
        "runtest_data",
        [
            {},
            {f"{_SCENARIO_PREFIX}-id": None},
            {f"{_SCENARIO_PREFIX}-text": None},
            {f"{_SCENARIO_PREFIX}-id": "123", f"{_SCENARIO_PREFIX}-text": None},
            {f"{_SCENARIO_PREFIX}-id": None, f"{_SCENARIO_PREFIX}-text": "123"},
        ],
    )
    def test_empty_data(
        self,
        test_rendered_featureview: mock.MagicMock,
        test_featureview_runtest_result: werkzeug.Response,
        flask_flash_handler_mock: mock.MagicMock,
        flask_urlfor_handler_mock: mock.MagicMock,
        redisproducer_addtask_mock: mock.MagicMock,
    ) -> None:
        flask_flash_handler_mock.assert_called_once_with("Scenario information not requested.", category="error")
        flask_urlfor_handler_mock.assert_not_called()
        redisproducer_addtask_mock.assert_not_called()
        assert test_featureview_runtest_result == test_rendered_featureview

    @pytest.mark.parametrize(
        "runtest_data", [{f"{_SCENARIO_PREFIX}-id": "8841", f"{_SCENARIO_PREFIX}-text": "smth"}],
    )
    def test_incorrect_scenario_data(
        self,
        test_rendered_featureview: mock.MagicMock,
        test_featureview_runtest_result: werkzeug.Response,
        flask_flash_handler_mock: mock.MagicMock,
        flask_urlfor_handler_mock: mock.MagicMock,
        redisproducer_addtask_mock: mock.MagicMock,
    ) -> None:
        flask_flash_handler_mock.assert_called_once_with(
            "Scenario does not exist, so could not run test.", category="error"
        )
        flask_urlfor_handler_mock.assert_not_called()
        redisproducer_addtask_mock.assert_not_called()
        assert test_featureview_runtest_result == test_rendered_featureview

    def test_correct_scenario_data(
        self,
        test_rendered_featureview: mock.MagicMock,
        test_featureview_runtest_result: werkzeug.Response,
        flask_flash_handler_mock: mock.MagicMock,
        flask_urlfor_handler_mock: mock.MagicMock,
        redisproducer_addtask_mock: mock.MagicMock,
        test_db_scenario: ScenarioModel,
    ) -> None:
        flask_flash_handler_mock.assert_not_called()
        flask_urlfor_handler_mock.assert_called_with("testrun.details_view", id=test_db_scenario.id)
        redisproducer_addtask_mock.assert_called_once_with(
            TestRunTask(data=TestRunData(test_run_id=test_db_scenario.id))
        )
        assert test_featureview_runtest_result != test_rendered_featureview

    def test_correct_run_created(
        self,
        test_featureview_runtest_result: werkzeug.Response,
        test_db_user: SystemUserModel,
        test_feature_container: FeatureTestContainer,
        test_db_scenario: ScenarioModel,
    ) -> None:
        with db.create_session() as session:
            db_test_run = session.query(db.TestRun).get(test_db_scenario.id)
            assert db_test_run is not None
            test_run: TestRunModel = TestRunModel.from_orm(db_test_run)
        assert test_run.id == test_db_scenario.id
        assert isinstance(test_run.created_at, datetime)
        assert test_run.name == test_feature_container.name
        assert test_run.executed_by == test_db_user.login
        assert test_run.status is db.TestRunStatus.STARTED
        assert test_run.start is None
        assert test_run.end is None
        assert test_run.report_status is db.TestReportStatus.EMPTY
        assert test_run.traceback is None
