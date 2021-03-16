from typing import cast

import pytest
from faker import Faker

from overhave import db
from overhave.entities.converters import EmulationModel, FeatureTypeModel, TestUserModel
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.storage.emulation import EmulationStorage


@pytest.fixture()
def test_emulation_settings() -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture()
def test_emulation_storage(test_emulation_settings: OverhaveEmulationSettings) -> EmulationStorage:
    return EmulationStorage(test_emulation_settings)


@pytest.fixture()
def _feature_type(faker: Faker) -> db.FeatureType:
    with db.create_session() as session:
        feature_type = db.FeatureType(name=cast(str, faker.word()))
        session.add(feature_type)
        session.flush()
        return cast(FeatureTypeModel, FeatureTypeModel.from_orm(feature_type))


@pytest.fixture()
def _test_user(faker: Faker, _feature_type: db.FeatureType) -> TestUserModel:
    with db.create_session() as session:
        test_user = db.TestUser(
            feature_type_id=_feature_type.id, name=cast(str, faker.word()), created_by=db.Role.admin
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_emulation(_test_user: db.TestUser, faker: Faker) -> EmulationModel:
    with db.create_session() as session:
        emulation = db.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=_test_user.id,
            created_by=db.Role.admin,
        )
        session.add(emulation)
        session.flush()
        return cast(EmulationModel, EmulationModel.from_orm(emulation))
