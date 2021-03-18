from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave import db
from overhave.entities.converters import (
    EmulationModel,
    FeatureModel,
    FeatureTypeModel,
    ScenarioModel,
    SystemUserModel,
    TestUserModel,
)
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.storage import TestRunStorage
from overhave.storage.emulation import EmulationStorage
from overhave.storage.feature_type import FeatureTypeStorage


@pytest.fixture(scope="class")
def test_emulation_settings() -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture(scope="class")
def test_emulation_storage(test_emulation_settings: OverhaveEmulationSettings) -> EmulationStorage:
    return EmulationStorage(test_emulation_settings)


@pytest.fixture()
def test_feature_type(database: None, faker: Faker) -> db.FeatureType:
    with db.create_session() as session:
        feature_type = db.FeatureType(name=cast(str, faker.word()))
        session.add(feature_type)
        session.flush()
        return cast(FeatureTypeModel, FeatureTypeModel.from_orm(feature_type))


@pytest.fixture()
def test_user_role(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_system_user(faker: Faker, test_user_role: db.Role) -> SystemUserModel:
    with db.create_session() as session:
        app_user = db.UserRole(login=faker.word(), password=faker.word(), role=test_user_role)
        session.add(app_user)
        session.flush()
        return cast(SystemUserModel, SystemUserModel.from_orm(app_user))


@pytest.fixture()
def test_user(test_system_user: SystemUserModel, faker: Faker, test_feature_type) -> TestUserModel:
    with db.create_session() as session:
        test_user = db.TestUser(
            feature_type_id=test_feature_type.id, name=cast(str, faker.word()), created_by=test_system_user.login
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_emulation(test_system_user: SystemUserModel, test_user: TestUserModel, faker: Faker) -> EmulationModel:
    with db.create_session() as session:
        emulation = db.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=test_user.id,
            created_by=test_system_user.login,
        )
        session.add(emulation)
        session.flush()
        return cast(EmulationModel, EmulationModel.from_orm(emulation))


@pytest.fixture()
def test_feature(faker: Faker, test_system_user: SystemUserModel, feature_type: FeatureTypeModel) -> FeatureModel:
    with db.create_session() as session:
        feature = db.Feature(
            name=faker.word(),
            author=test_system_user.login,
            type_id=feature_type.id,
            task=[faker.sentence()],
            last_edited_by=test_system_user.login,
            released=False,
        )
        session.add(feature)
        session.flush()
        return cast(FeatureModel, feature)


@pytest.fixture()
def test_scenario(faker: Faker, test_feature: FeatureModel) -> ScenarioModel:
    with db.create_session() as session:
        scenario = db.Scenario(feature_id=test_feature.id, text=faker.sentence())
        session.add(scenario)
        session.flush()
        return cast(ScenarioModel, scenario)


@pytest.fixture(scope="class")
def test_test_run_storage():
    return TestRunStorage()


@pytest.fixture(scope="class")
def test_feature_type_storage():
    return FeatureTypeStorage()
