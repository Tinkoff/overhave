from datetime import datetime
from typing import List

from pydantic.main import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from overhave.db.tables import Emulation, EmulationRun, Feature, FeatureType, Scenario, TestRun, TestUser
from overhave.db.utils import create_session


class FeatureTypeModel(sqlalchemy_to_pydantic(FeatureType)):  # type: ignore
    name: str


class FeatureModel(sqlalchemy_to_pydantic(Feature)):  # type: ignore
    name: str
    author: str
    feature_type: FeatureTypeModel
    last_edited_by: str
    task: List[str]


class ScenarioModel(sqlalchemy_to_pydantic(Scenario)):  # type: ignore
    text: str


class TestRunModel(sqlalchemy_to_pydantic(TestRun)):  # type: ignore
    id: int
    executed_by: str
    start: datetime


class BaseProcessingContext(BaseModel):
    feature: FeatureModel
    scenario: ScenarioModel


class ProcessingContext(BaseProcessingContext):
    feature: FeatureModel
    scenario: ScenarioModel
    test_run: TestRunModel


class TestUserModel(sqlalchemy_to_pydantic(TestUser)):  # type: ignore
    feature_type: FeatureTypeModel


class EmulationModel(sqlalchemy_to_pydantic(Emulation)):  # type: ignore
    test_user: TestUserModel


class EmulationRunModel(sqlalchemy_to_pydantic(EmulationRun)):  # type: ignore
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
