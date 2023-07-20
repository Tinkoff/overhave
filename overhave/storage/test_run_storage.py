import abc
from typing import Any, cast

import sqlalchemy as sa
import sqlalchemy.orm as so

from overhave import db
from overhave.storage.converters import TestRunModel
from overhave.utils import get_current_time


class ITestRunStorage(abc.ABC):
    """Abstract class for test runs storage."""

    @abc.abstractmethod
    def create_testrun(self, scenario_id: int, executed_by: str) -> int:
        pass

    @abc.abstractmethod
    def set_run_status(self, run_id: int, status: db.TestRunStatus, traceback: str | None = None) -> None:
        pass

    @abc.abstractmethod
    def set_report(self, run_id: int, status: db.TestReportStatus, report: str | None = None) -> None:
        pass

    @abc.abstractmethod
    def testrun_model_by_id(self, session: so.Session, run_id: int) -> TestRunModel:
        pass

    @abc.abstractmethod
    def get_testrun_model(self, run_id: int) -> TestRunModel | None:
        pass


class TestRunStorage(ITestRunStorage):
    """Class for test runs storage."""

    def create_testrun(self, scenario_id: int, executed_by: str) -> int:
        with db.create_session() as session:
            scenario: db.Scenario = session.query(db.Scenario).filter(db.Scenario.id == scenario_id).one()
            run = db.TestRun(
                scenario_id=scenario_id,
                name=scenario.feature.name,
                status=db.TestRunStatus.STARTED,
                report_status=db.TestReportStatus.EMPTY,
                executed_by=executed_by,
            )
            session.add(run)
            session.flush()
            return cast(int, run.id)

    def set_run_status(self, run_id: int, status: db.TestRunStatus, traceback: str | None = None) -> None:
        with db.create_session() as session:
            values: dict[str, Any] = {"status": status}
            if status == db.TestRunStatus.RUNNING:
                values["start"] = get_current_time()
            if status.finished:
                values["end"] = get_current_time()
            if isinstance(traceback, str):
                values["traceback"] = traceback

            session.execute(sa.update(db.TestRun).where(db.TestRun.id == run_id).values(**values))

    def set_report(self, run_id: int, status: db.TestReportStatus, report: str | None = None) -> None:
        with db.create_session() as session:
            values: dict[str, Any] = {"report_status": status}
            if isinstance(report, str):
                values["report"] = report

            session.execute(sa.update(db.TestRun).where(db.TestRun.id == run_id).values(**values))

    def testrun_model_by_id(self, session: so.Session, run_id: int) -> TestRunModel:
        run = session.query(db.TestRun).filter(db.TestRun.id == run_id).one()
        return TestRunModel.model_validate(run)

    def get_testrun_model(self, run_id: int) -> TestRunModel | None:
        with db.create_session() as session:
            run = session.get(db.TestRun, run_id)
            if run is None:
                return None
            return TestRunModel.model_validate(run)
