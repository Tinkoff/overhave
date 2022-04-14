import datetime
import socket
from typing import cast
from unittest import mock
from uuid import uuid1

import pytest
from faker import Faker

from overhave import db
from overhave.db import DraftStatus
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.storage import (
    DraftModel,
    DraftStorage,
    EmulationModel,
    EmulationStorage,
    FeatureModel,
    FeatureStorage,
    FeatureTagStorage,
    FeatureTypeModel,
    FeatureTypeStorage,
    ScenarioModel,
    ScenarioStorage,
    SystemUserModel,
    TagModel,
    TestRunStorage,
)


@pytest.fixture(scope="module")
def socket_mock() -> mock.MagicMock:
    with mock.patch("socket.socket", return_value=mock.create_autospec(socket.socket)) as mocked_socket:
        yield mocked_socket


@pytest.fixture(scope="class")
def test_emulation_settings() -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture(scope="class")
def test_emulation_storage(
    socket_mock: mock.MagicMock, test_emulation_settings: OverhaveEmulationSettings
) -> EmulationStorage:
    return EmulationStorage(test_emulation_settings)


@pytest.fixture()
def test_emulation(test_system_user: SystemUserModel, test_testuser, faker: Faker) -> EmulationModel:
    with db.create_session() as session:
        emulation = db.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=test_testuser.id,
            created_by=test_system_user.login,
        )
        session.add(emulation)
        session.flush()
        return cast(EmulationModel, EmulationModel.from_orm(emulation))


@pytest.fixture(scope="class")
def test_run_storage() -> TestRunStorage:
    return TestRunStorage()


@pytest.fixture(scope="class")
def test_tag_storage() -> FeatureTagStorage:
    return FeatureTagStorage()


@pytest.fixture(scope="class")
def test_feature_storage(test_tag_storage: FeatureTagStorage) -> FeatureStorage:
    return FeatureStorage(tag_storage=test_tag_storage)


@pytest.fixture(scope="class")
def test_feature_type_storage() -> FeatureTypeStorage:
    return FeatureTypeStorage()


@pytest.fixture()
def test_feature(test_system_user: SystemUserModel, test_feature_type: FeatureTypeModel, faker: Faker) -> FeatureModel:
    with db.create_session() as session:
        feature = db.Feature(
            name=faker.word(),
            author=test_system_user.login,
            type_id=test_feature_type.id,
            task=[faker.word()[:11]],
            file_path=f"{faker.word()}/{faker.word()}",
        )
        session.add(feature)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_feature_with_tag(test_feature: FeatureModel, test_tag: TagModel) -> FeatureModel:
    with db.create_session() as session:
        tag = session.query(db.Tags).filter(db.Tags.id == test_tag.id).one()
        feature = session.query(db.Feature).filter(db.Feature.id == test_feature.id).one()
        feature.feature_tags.append(tag)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture(scope="class")
def test_scenario_storage() -> ScenarioStorage:
    return ScenarioStorage()


@pytest.fixture()
def test_scenario(test_feature: FeatureModel, faker: Faker) -> ScenarioModel:
    with db.create_session() as session:
        db_scenario = db.Scenario(feature_id=test_feature.id, text=faker.word())
        session.add(db_scenario)
        session.flush()
        return cast(ScenarioModel, ScenarioModel.from_orm(db_scenario))


@pytest.fixture(scope="class")
def test_report() -> str:
    return uuid1().hex


@pytest.fixture()
def test_created_test_run_id(
    test_run_storage: TestRunStorage, test_scenario: ScenarioModel, test_feature: FeatureModel
) -> int:
    return test_run_storage.create_test_run(test_scenario.id, test_feature.author)


@pytest.fixture()
def test_second_created_test_run_id(
    test_run_storage: TestRunStorage, test_scenario: ScenarioModel, test_feature: FeatureModel
) -> int:
    return test_run_storage.create_test_run(test_scenario.id, test_feature.author)


@pytest.fixture(scope="class")
def test_draft_storage() -> DraftStorage:
    return DraftStorage()


@pytest.fixture()
def test_draft(
    faker: Faker, test_feature: FeatureModel, test_created_test_run_id: int, test_system_user: SystemUserModel
) -> DraftModel:
    with db.create_session() as session:
        draft: db.Draft = db.Draft(
            feature_id=test_feature.id,
            test_run_id=test_created_test_run_id,
            text=faker.word(),
            published_by=test_system_user.login,
            status=DraftStatus.REQUESTED,
        )
        draft.pr_url = faker.word()
        draft.published_at = datetime.datetime.now()
        session.add(draft)
        session.flush()
        return cast(DraftModel, DraftModel.from_orm(draft))


@pytest.fixture()
def test_user_name(faker: Faker) -> str:
    return faker.word()
