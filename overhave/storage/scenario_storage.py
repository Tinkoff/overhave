import abc
from typing import Optional, cast

from overhave import db
from overhave.storage.converters import ScenarioModel


class BaseScenarioStorageException(Exception):
    """Base exception for :class:`ScenarioStorage`."""


class ScenarioNotExistsError(BaseScenarioStorageException):
    """Exception for situation without scenario."""


class IScenarioStorage(abc.ABC):
    """Abstract class for feature type storage."""

    @staticmethod
    @abc.abstractmethod
    def get_scenario(scenario_id: int) -> Optional[ScenarioModel]:
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
    def get_scenario(scenario_id: int) -> Optional[ScenarioModel]:
        with db.create_session() as session:
            scenario: Optional[db.Scenario] = session.query(db.Scenario).get(scenario_id)
            if scenario is not None:
                return cast(ScenarioModel, ScenarioModel.from_orm(scenario))
            return None

    @staticmethod
    def get_scenario_by_feature_id(feature_id: int) -> ScenarioModel:
        with db.create_session() as session:
            scenario: db.Scenario = session.query(db.Scenario).filter(db.Scenario.feature_id == feature_id).one()
            return cast(ScenarioModel, ScenarioModel.from_orm(scenario))

    @staticmethod
    def update_scenario(model: ScenarioModel) -> None:
        with db.create_session() as session:
            scenario: db.Scenario = session.query(db.Scenario).get(model.id)
            if scenario is None:
                raise ScenarioNotExistsError(f"Scenario with id={model.id} does not exist!")
            scenario.text = model.text

    @staticmethod
    def create_scenario(model: ScenarioModel) -> int:
        with db.create_session() as session:
            scenario = db.Scenario(feature_id=model.feature_id, text=model.text)  # type: ignore
            session.add(scenario)
            session.flush()
            return cast(int, scenario.id)
