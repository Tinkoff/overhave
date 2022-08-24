import datetime
import socket
from typing import cast
from unittest import mock

import pytest
from faker import Faker

from overhave import db
from overhave.db import DraftStatus
from overhave.storage import (
    DraftModel,
    DraftStorage,
    FeatureModel,
    FeatureStorage,
    FeatureTagStorage,
    FeatureTypeStorage,
    ScenarioModel,
    SystemUserModel,
    TestRunStorage,
)


@pytest.fixture(scope="class")
def socket_mock() -> mock.MagicMock:
    with mock.patch("socket.socket", return_value=mock.create_autospec(socket.socket)) as mocked_socket:
        yield mocked_socket


@pytest.fixture(scope="class")
def test_tag_storage() -> FeatureTagStorage:
    return FeatureTagStorage()


@pytest.fixture(scope="class")
def test_feature_storage(test_tag_storage: FeatureTagStorage) -> FeatureStorage:
    return FeatureStorage()


@pytest.fixture(scope="class")
def test_feature_type_storage() -> FeatureTypeStorage:
    return FeatureTypeStorage()


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
def test_user_key(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_user_name(faker: Faker) -> str:
    return faker.word()
