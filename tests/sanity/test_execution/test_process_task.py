from datetime import datetime
from unittest import mock

import pytest

from demo.settings import OverhaveDemoAppLanguage
from overhave import db
from overhave.storage import TestRunModel


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_demo_language", [OverhaveDemoAppLanguage.RU], indirect=True)
class TestOverhaveTestExecution:
    """Sanity tests for application test run."""

    @pytest.mark.parametrize(
        ("run_test_process_result", "report_status"),
        [(0, db.TestReportStatus.GENERATED), (1, db.TestReportStatus.GENERATION_FAILED)],
        indirect=True,
    )
    def test_correct_run_executed(
        self, test_executed_testruntask_id: int, subprocess_run_mock: mock.MagicMock, report_status: db.TestReportStatus
    ) -> None:
        subprocess_run_mock.assert_called_once()
        with db.create_session() as session:
            db_test_run = session.get(db.TestRun, test_executed_testruntask_id)
            assert db_test_run is not None
            test_run: TestRunModel = TestRunModel.from_orm(db_test_run)
        assert test_run.id == test_executed_testruntask_id
        assert isinstance(test_run.created_at, datetime)
        assert test_run.status is db.TestRunStatus.SUCCESS
        assert isinstance(test_run.start, datetime)
        assert isinstance(test_run.end, datetime)
        assert test_run.report_status is report_status
        assert test_run.traceback is None
