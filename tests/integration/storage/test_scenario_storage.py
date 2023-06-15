import allure
import pytest
from faker import Faker

from overhave import db
from overhave.storage import FeatureModel, ScenarioModel, ScenarioStorage
from tests.db_utils import count_queries, create_test_session


def _check_base_scenario_type_model(test_model: ScenarioModel | db.Scenario, validation_model: ScenarioModel) -> None:
    assert test_model.id == validation_model.id
    assert test_model.text == validation_model.text
    assert test_model.feature_id == validation_model.feature_id


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
@pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
class TestScenarioStorage:
    """Integration tests for :class:`ScenarioStorage`."""

    def test_scenario_model_by_id(self, test_scenario_storage: ScenarioStorage, test_scenario: ScenarioModel) -> None:
        with count_queries(1):
            with db.create_session() as session:
                model = test_scenario_storage.scenario_model_by_id(session=session, scenario_id=test_scenario.id)
        assert isinstance(model, ScenarioModel)
        _check_base_scenario_type_model(test_model=model, validation_model=test_scenario)

    def test_get_scenario_by_feature_id(
        self, test_scenario_storage: ScenarioStorage, test_scenario: ScenarioModel
    ) -> None:
        with count_queries(1):
            model = test_scenario_storage.get_scenario_by_feature_id(test_scenario.feature_id)
        assert model is not None
        _check_base_scenario_type_model(test_model=model, validation_model=test_scenario)

    def test_update_scenario(
        self,
        test_scenario_storage: ScenarioStorage,
        test_scenario: ScenarioModel,
        faker: Faker,
    ) -> None:
        new_model = ScenarioModel(id=test_scenario.feature_id, text=faker.word(), feature_id=test_scenario.feature_id)
        with count_queries(1):
            test_scenario_storage.update_scenario(new_model)
        with create_test_session() as session:
            changed_model = session.get(db.Scenario, new_model.id)
            assert changed_model is not None
            _check_base_scenario_type_model(test_model=changed_model, validation_model=new_model)

    def test_create_scenario(
        self,
        test_scenario_storage: ScenarioStorage,
        faker: Faker,
        test_feature: FeatureModel,
    ) -> None:
        new_model = ScenarioModel(id=0, text=faker.word(), feature_id=test_feature.id)
        with count_queries(1):
            new_model.id = test_scenario_storage.create_scenario(new_model)
        with create_test_session() as session:
            created_model = session.get(db.Scenario, new_model.id)
            assert created_model is not None
            _check_base_scenario_type_model(test_model=created_model, validation_model=new_model)
