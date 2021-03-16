from datetime import datetime
from unittest import mock

from overhave import db
from overhave.entities import ScenarioModel, SystemUserModel, TestRunModel
from overhave.factory import ProxyFactory
from tests.objects import FeatureTestContainer


class TestOverhaveRunTest:
    """ Sanity tests for application test run. """

    def test_redirect_to_run(
        self,
        test_factory_after_run: ProxyFactory,
        flask_urlfor_handler_mock: mock.MagicMock,
        test_db_scenario: ScenarioModel,
    ):
        flask_urlfor_handler_mock.assert_called_with("testrun.details_view", id=test_db_scenario.id)

    def test_run_exists(
        self,
        test_factory_after_run: ProxyFactory,
        test_db_user: SystemUserModel,
        test_feature_container: FeatureTestContainer,
        test_db_scenario: ScenarioModel,
    ):
        with db.create_session() as session:
            db_test_run = session.query(db.TestRun).filter(db.TestRun.scenario_id == test_db_scenario.id).one()
            test_run: TestRunModel = TestRunModel.from_orm(db_test_run)
        assert test_run.id == test_db_scenario.id
        assert test_run.name == test_feature_container.name
        assert test_run.executed_by == test_db_user.login
        assert test_run.status is db.TestRunStatus.SUCCESS
        assert isinstance(test_run.start, datetime)
        assert isinstance(test_run.end, datetime)
        assert test_run.report_status is db.TestReportStatus.GENERATED
        assert test_run.traceback is None
