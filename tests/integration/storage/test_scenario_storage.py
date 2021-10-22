import pytest
from faker import Faker

from overhave import db
from overhave.entities import FeatureModel, ScenarioModel
from overhave.storage import ScenarioStorage


def _check_base_scenario_type_model(test_model: ScenarioModel, validation_model: ScenarioModel) -> None:
    assert test_model.id == validation_model.id
    assert test_model.text == validation_model.text
    assert test_model.feature_id == validation_model.feature_id


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
class TestScenarioStorage:
    """ Integration tests for :class:`ScenarioStorage`. """

    def test_get_scenario(self, test_scenario_storage: ScenarioStorage, test_scenario: ScenarioModel) -> None:
        model = test_scenario_storage.get_scenario(test_scenario.id)
        assert model is not None
        _check_base_scenario_type_model(test_model=model, validation_model=test_scenario)

    def test_get_scenario_by_feature_id(
        self, test_scenario_storage: ScenarioStorage, test_scenario: ScenarioModel
    ) -> None:
        model = test_scenario_storage.get_scenario_by_feature_id(test_scenario.feature_id)
        assert model is not None
        _check_base_scenario_type_model(test_model=model, validation_model=test_scenario)

    def test_update_scenario(
        self, test_scenario_storage: ScenarioStorage, test_scenario: ScenarioModel, faker: Faker,
    ) -> None:
        new_model = ScenarioModel(id=test_scenario.feature_id, text=faker.word(), feature_id=test_scenario.feature_id)
        test_scenario_storage.update_scenario(new_model)
        changed_model = test_scenario_storage.get_scenario(new_model.id)
        assert changed_model is not None
        _check_base_scenario_type_model(test_model=changed_model, validation_model=new_model)

    def test_create_scenario(
        self, test_scenario_storage: ScenarioStorage, faker: Faker, test_feature: FeatureModel,
    ) -> None:
        new_model = ScenarioModel(id=0, text=faker.word(), feature_id=test_feature.id)
        new_model.id = test_scenario_storage.create_scenario(new_model)
        created_model = test_scenario_storage.get_scenario(new_model.id)
        assert created_model is not None
        _check_base_scenario_type_model(test_model=created_model, validation_model=new_model)
