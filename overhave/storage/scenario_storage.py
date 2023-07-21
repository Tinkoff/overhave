import abc
from typing import cast

import sqlalchemy as sa
import sqlalchemy.orm as so

from overhave import db
from overhave.storage.converters import ScenarioModel


class IScenarioStorage(abc.ABC):
    """Abstract class for feature type storage."""

    @staticmethod
    @abc.abstractmethod
    def scenario_model_by_id(session: so.Session, scenario_id: int) -> ScenarioModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_scenario_by_feature_id(feature_id: int) -> ScenarioModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def update_scenario(model: ScenarioModel) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_scenario(model: ScenarioModel) -> int:
        pass


class ScenarioStorage(IScenarioStorage):
    """Class for feature type storage."""

    @staticmethod
    def scenario_model_by_id(session: so.Session, scenario_id: int) -> ScenarioModel:
        scenario = session.query(db.Scenario).filter(db.Scenario.id == scenario_id).one()
        return ScenarioModel.model_validate(scenario)

    @staticmethod
    def get_scenario_by_feature_id(feature_id: int) -> ScenarioModel:
        with db.create_session() as session:
            scenario: db.Scenario = session.query(db.Scenario).filter(db.Scenario.feature_id == feature_id).one()
            return ScenarioModel.model_validate(scenario)

    @staticmethod
    def update_scenario(model: ScenarioModel) -> None:
        with db.create_session() as session:
            session.execute(sa.update(db.Scenario).where(db.Scenario.id == model.id).values(text=model.text))

    @staticmethod
    def create_scenario(model: ScenarioModel) -> int:
        with db.create_session() as session:
            scenario = db.Scenario(feature_id=model.feature_id, text=model.text)
            session.add(scenario)
            session.flush()
            return cast(int, scenario.id)
