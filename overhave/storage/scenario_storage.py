import abc
from typing import Optional, cast

from overhave import db
from overhave.entities import ScenarioModel


class IScenarioStorage(abc.ABC):
    """ Abstract class for feature type storage. """

    @abc.abstractmethod
    def get_scenario(self, scenario_id: int) -> Optional[ScenarioModel]:
        pass


class ScenarioStorage(IScenarioStorage):
    """ Class for feature type storage. """

    def get_scenario(self, scenario_id: int) -> Optional[ScenarioModel]:
        with db.create_session() as session:
            scenario: Optional[db.Scenario] = session.query(db.Scenario).get(scenario_id)
            if scenario is not None:
                return cast(ScenarioModel, ScenarioModel.from_orm(scenario))
            return None
