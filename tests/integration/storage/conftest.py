import pytest
from overhave.entities.settings import OverhaveEmulationSettings
import overhave.storage.emulation as e
from faker import Faker
from overhave import db

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
    feature_type = db.tables.FeatureType(name=faker.word())
    test_user = db.tables.TestUser(created_by=ADMIN, feature_type_id=feature_type.id, name=faker.word())
    emulation: db.tables.Emulation = db.tables.Emulation(
        name=faker.word(), command=faker.word(), created_by=ADMIN, test_user_id=test_user.id
    )
    with db.create_session() as session:
        session.add(feature_type)
        session.add(test_user)
        session.add(emulation)
        session.flush()
    return emulation.id
