import pytest
from faker import Faker

import overhave.storage.emulation as e
from overhave import db
from overhave.entities.settings import OverhaveEmulationSettings

ADMIN = "admin"


@pytest.fixture()
def test_emulation_settings() -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture()
def test_emulation_storage(test_emulation_settings) -> e.EmulationStorage:
    return e.EmulationStorage(test_emulation_settings)


@pytest.fixture()
def test_add_emulation_to_db():
    faker = Faker()
    with db.create_session() as session:
        feature_type = db.tables.FeatureType(name=faker.word())
        session.add(feature_type)
        test_user = db.tables.TestUser(created_by=ADMIN, feature_type_id=feature_type.id, name=faker.word())
        session.add(test_user)
        emulation: db.tables.Emulation = db.tables.Emulation(
            name=faker.word(), command=faker.word(), created_by=ADMIN, test_user_id=test_user.id
        )
        session.add(emulation)
    return emulation.id
