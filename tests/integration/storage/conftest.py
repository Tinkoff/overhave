from typing import cast

import pytest
from faker import Faker

from overhave import db
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.storage.emulation import EmulationStorage


@pytest.fixture()
def test_emulation_settings() -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture()
def test_emulation_storage(test_emulation_settings) -> EmulationStorage:
    return EmulationStorage(test_emulation_settings)


def give_id_of_table(table):
    with db.create_session() as session:
        session.add(table)
        session.flush()
        session.commit()
    return table.id


@pytest.fixture()
def test_feature_type_id(faker: Faker) -> int:
    return give_id_of_table(db.tables.FeatureType(name=cast(str, faker.word())))


@pytest.fixture()
def test_user_id(faker: Faker) -> int:
    return give_id_of_table(
        db.tables.TestUser(feature_type_id=test_feature_type_id, name=cast(str, faker.word()))
    )


@pytest.fixture()
def test_emulation_id(faker: Faker) -> int:
    return give_id_of_table(
        db.tables.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=test_user_id,
        )
    )


@pytest.fixture()
def test_emulation_run(test_emulation_storage: EmulationStorage, test_emulation_id: int) -> db.EmulationRun:
    return test_emulation_storage.create_emulation_run(emulation_id=test_emulation_id, initiated_by=db.Role.admin)


def commit_emulation_run(emulation_run) -> None:
    with db.create_session() as session:
        session.add(emulation_run)
        session.flush()
        session.commit()
