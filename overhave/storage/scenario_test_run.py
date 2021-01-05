from typing import cast

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
            executed_by=executed_by,
        )
        session.add(run)
        session.flush()
        return cast(int, run.id)


def set_run_status(run_id: int, status: db.TestRunStatus) -> None:
    with db.create_session() as session:
        run = cast(db.TestRun, session.query(db.TestRun).filter(db.TestRun.id == run_id).one())
        run.status = status


def save_draft(run_id: int) -> int:
    with db.create_session() as session:
        draft = session.query(db.Draft).as_unique(test_run_id=run_id)
        session.add(draft)
        session.flush()
        return cast(int, draft.id)


def set_report(run_id: int, report: str) -> None:
    with db.create_session() as session:
        run = cast(db.TestRun, session.query(db.TestRun).filter(db.TestRun.id == run_id).one())
        run.report = report
        run.end = get_current_time()


def set_traceback(run_id: int, traceback: str) -> None:
    with db.create_session() as session:
        run = cast(db.TestRun, session.query(db.TestRun).filter(db.TestRun.id == run_id).one())
        run.traceback = traceback
