from typing import Optional, cast

from overhave import db
from overhave.utils.time import get_current_time


def create_test_run(scenario_id: int, executed_by: str) -> int:
    with db.create_session() as session:
        scenario = cast(db.Scenario, session.query(db.Scenario).filter(db.Scenario.id == scenario_id).one())
        feature = cast(db.Feature, session.query(db.Feature).filter(db.Feature.id == scenario.feature_id).one())
        run = db.TestRun(  # type: ignore
            scenario_id=scenario_id,
            name=feature.name,
            start=get_current_time(),
            status=db.TestRunStatus.STARTED,
            report_status=db.TestReportStatus.EMPTY,
            executed_by=executed_by,
        )
        session.add(run)
        session.flush()
        return cast(int, run.id)


def set_run_status(run_id: int, status: db.TestRunStatus) -> None:
    with db.create_session() as session:
        run = cast(db.TestRun, session.query(db.TestRun).filter(db.TestRun.id == run_id).one())
        run.status = status
        if status.finished:
            run.end = get_current_time()


def set_report(run_id: int, status: db.TestReportStatus, report: Optional[str] = None) -> None:
    with db.create_session() as session:
        run = cast(db.TestRun, session.query(db.TestRun).filter(db.TestRun.id == run_id).one())
        run.report_status = status
        if isinstance(report, str):
            run.report = report


def set_traceback(run_id: int, traceback: str) -> None:
    with db.create_session() as session:
        run = cast(db.TestRun, session.query(db.TestRun).filter(db.TestRun.id == run_id).one())
        run.traceback = traceback
