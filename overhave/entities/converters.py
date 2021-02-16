from datetime import datetime
from typing import List

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from overhave.db import (
    Emulation,
    EmulationRun,
    Feature,
    FeatureType,
    Scenario,
    TestReportStatus,
    TestRun,
    TestRunStatus,
    TestUser,
    create_session,
)
from overhave.entities.feature import FeatureTypeName


class FeatureTypeModel(sqlalchemy_to_pydantic(FeatureType)):  # type: ignore
    """ Model for :class:`FeatureType` row. """

    name: FeatureTypeName


class FeatureModel(sqlalchemy_to_pydantic(Feature)):  # type: ignore
    """ Model for :class:`Feature` row. """

    name: str
    author: str
    feature_type: FeatureTypeModel
    last_edited_by: str
    task: List[str]


class ScenarioModel(sqlalchemy_to_pydantic(Scenario)):  # type: ignore
    """ Model for :class:`Scenario` row. """

    text: str


class TestRunModel(sqlalchemy_to_pydantic(TestRun)):  # type: ignore
    """ Model for :class:`TestRun` row. """

    id: int
    executed_by: str
    start: datetime
    status: TestRunStatus
    report_status: TestReportStatus


class ProcessingContext(BaseModel):
    """ Model for simple processing entities usage. """

    feature: FeatureModel
    scenario: ScenarioModel
    test_run: TestRunModel


class TestUserModel(sqlalchemy_to_pydantic(TestUser)):  # type: ignore
    """ Model for :class:`TestUser` row. """

    feature_type: FeatureTypeModel


class EmulationModel(sqlalchemy_to_pydantic(Emulation)):  # type: ignore
    """ Model for :class:`Emulation` row. """

    test_user: TestUserModel


class EmulationRunModel(sqlalchemy_to_pydantic(EmulationRun)):  # type: ignore
    """ Model for :class:`EmulationRun` row. """

    emulation: EmulationModel


def get_context_by_test_run_id(test_run_id: int) -> ProcessingContext:
    with create_session() as session:
        db_test_run = session.query(TestRun).filter_by(id=test_run_id).one()
        db_scenario = session.query(Scenario).filter_by(id=db_test_run.scenario.id).one()
        db_feature = session.query(Feature).filter_by(id=db_scenario.feature.id).one()
        return ProcessingContext(
            feature=FeatureModel.from_orm(db_feature),
            scenario=ScenarioModel.from_orm(db_scenario),
            test_run=TestRunModel.from_orm(db_test_run),
        )
