import abc
from typing import cast

from overhave import db
from overhave.entities import ScenarioModel


class IScenarioStorage(abc.ABC):
    """ Abstract class for feature type storage. """

    @abc.abstractmethod
    def get_scenario(self, scenario_id: int) -> ScenarioModel:
        pass


class ScenarioStorage(IScenarioStorage):
    """ Class for feature type storage. """

    def get_scenario(self, scenario_id: int) -> ScenarioModel:
        with db.create_session() as session:
            scenario: db.Scenario = session.query(db.Scenario).filter(db.Scenario.id == scenario_id).one()
            return cast(ScenarioModel, ScenarioModel.from_orm(scenario))
