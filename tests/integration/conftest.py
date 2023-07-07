from datetime import datetime
from typing import cast
from uuid import uuid1

import allure
import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave import OverhaveEmulationSettings, db
from overhave.db import DraftStatus
from overhave.storage import (
    DraftModel,
    DraftStorage,
    EmulationModel,
    EmulationRunModel,
    EmulationStorage,
    FeatureModel,
    FeatureStorage,
    FeatureTypeModel,
    ScenarioModel,
    ScenarioStorage,
    SystemUserGroupStorage,
    SystemUserModel,
    SystemUserStorage,
    TagModel,
    TestRunStorage,
    TestUserModel,
    TestUserSpecification,
    TestUserStorage,
)
from overhave.utils import get_current_time
from tests.db_utils import create_test_session


@pytest.fixture(scope="module")
def test_system_user_storage() -> SystemUserStorage:
    return SystemUserStorage()


@pytest.fixture(scope="module")
def test_system_user_group_storage() -> SystemUserGroupStorage:
    return SystemUserGroupStorage()


@pytest.fixture(scope="module")
def test_user_storage() -> TestUserStorage:
    return TestUserStorage()


@pytest.fixture(scope="module")
def test_scenario_storage() -> ScenarioStorage:
    return ScenarioStorage()


@pytest.fixture(scope="module")
def test_run_storage() -> TestRunStorage:
    return TestRunStorage()


@pytest.fixture(scope="class")
def test_draft_storage() -> DraftStorage:
    return DraftStorage()


@pytest.fixture(scope="class")
def test_feature_storage() -> FeatureStorage:
    return FeatureStorage()


@pytest.fixture(scope="module")
def test_emulation_storage(emulation_settings: OverhaveEmulationSettings) -> EmulationStorage:
    return EmulationStorage(emulation_settings)


@pytest.fixture()
def test_feature_type(database: None, faker: Faker) -> FeatureTypeModel:
    with create_test_session() as session:
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
def service_system_user(
    test_system_user_storage: SystemUserStorage,
    database: None,
    test_user_role: db.Role,
    faker: Faker,
) -> SystemUserModel:
    with create_test_session() as session:
        db_user = db.UserRole(login=f"{faker.word()}_{faker.word()}", password=faker.word(), role=test_user_role)
        session.add(db_user)
        session.flush()
        return SystemUserModel.from_orm(db_user)


@pytest.fixture()
def test_specification() -> TestUserSpecification:
    return TestUserSpecification({"test": "value"})


@pytest.fixture()
def testuser_allow_update(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return request.param
    return False


@pytest.fixture()
def test_testuser(
    service_system_user: SystemUserModel,
    faker: Faker,
    test_feature_type,
    test_specification: TestUserSpecification,
    testuser_allow_update: bool,
) -> TestUserModel:
    with create_test_session() as session:
        test_user = db.TestUser(
            feature_type_id=test_feature_type.id,
            key=cast(str, faker.word()),
            name=cast(str, faker.word()),
            created_by=service_system_user.login,
            specification=test_specification,
            allow_update=testuser_allow_update,
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_tag(service_system_user: SystemUserModel, faker: Faker) -> TagModel:
    with create_test_session() as session:
        tag = db.Tags(value=faker.word(), created_by=service_system_user.login)
        session.add(tag)
        session.flush()
        return cast(TagModel, TagModel.from_orm(tag))


@pytest.fixture()
def test_severity(request: FixtureRequest) -> allure.severity_level:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_feature(
    service_system_user: SystemUserModel,
    test_feature_type: FeatureTypeModel,
    test_severity: allure.severity_level,
    faker: Faker,
) -> FeatureModel:
    with create_test_session() as session:
        feature = db.Feature(
            name=faker.word(),
            author=service_system_user.login,
            type_id=test_feature_type.id,
            task=[faker.word()[:11]],
            file_path=f"{faker.word()}/{faker.word()}",
            severity=test_severity,
            last_edited_at=get_current_time(),
            last_edited_by=service_system_user.login,
        )
        session.add(feature)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_features(
    service_system_user: SystemUserModel,
    test_feature_type: FeatureTypeModel,
    test_severity: allure.severity_level,
    faker: Faker,
    num_features: int = 2,
) -> list[FeatureModel]:
    features = []
    with create_test_session() as session:
        for x in range(num_features):
            feature = db.Feature(
                name=faker.word(),
                author=service_system_user.login,
                type_id=test_feature_type.id,
                task=[faker.word()[:11]],
                file_path=f"{faker.word()}/{faker.word()}",
                severity=test_severity,
                last_edited_at=get_current_time(),
                last_edited_by=service_system_user.login,
            )
            session.add(feature)
            session.flush()
            features.append(cast(FeatureModel, FeatureModel.from_orm(feature)))
    return features


@pytest.fixture()
def test_feature_with_tag(test_feature: FeatureModel, test_tag: TagModel) -> FeatureModel:
    with create_test_session() as session:
        tag = session.query(db.Tags).filter(db.Tags.id == test_tag.id).one()
        feature = session.query(db.Feature).filter(db.Feature.id == test_feature.id).one()
        feature.feature_tags.append(tag)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_features_with_tag(test_features: list[FeatureModel], test_tag: TagModel) -> list[FeatureModel]:
    features = []
    with create_test_session() as session:
        tag = session.query(db.Tags).filter(db.Tags.id == test_tag.id).one()
        for test_feature in test_features:
            feature = session.query(db.Feature).filter(db.Feature.id == test_feature.id).one()
            feature.feature_tags.append(tag)
            session.flush()
            features.append(cast(FeatureModel, FeatureModel.from_orm(feature)))
    return features


@pytest.fixture()
def test_scenario(test_feature: FeatureModel, faker: Faker) -> ScenarioModel:
    with create_test_session() as session:
        db_scenario = db.Scenario(feature_id=test_feature.id, text=faker.word())
        session.add(db_scenario)
        session.flush()
        return cast(ScenarioModel, ScenarioModel.from_orm(db_scenario))


@pytest.fixture()
def test_created_test_run_id(
    test_run_storage: TestRunStorage,
    test_feature: FeatureModel,
    test_scenario: ScenarioModel,
) -> int:
    with create_test_session():
        return test_run_storage.create_testrun(test_scenario.id, test_feature.author)


@pytest.fixture()
def test_scenarios(test_features: list[FeatureModel], faker: Faker) -> list[ScenarioModel]:
    scenarios = []
    with create_test_session() as session:
        for test_feature in test_features:
            db_scenario = db.Scenario(feature_id=test_feature.id, text=faker.word())
            session.add(db_scenario)
            session.flush()
        scenarios.append(cast(ScenarioModel, ScenarioModel.from_orm(db_scenario)))
    return scenarios


@pytest.fixture()
def test_report() -> str:
    return uuid1().hex


@pytest.fixture()
def test_emulation(service_system_user: SystemUserModel, test_testuser, faker: Faker) -> EmulationModel:
    with create_test_session() as session:
        emulation = db.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=test_testuser.id,
            created_by=service_system_user.login,
        )
        session.add(emulation)
        session.flush()
        return cast(EmulationModel, EmulationModel.from_orm(emulation))


@pytest.fixture()
def test_emulation_run(service_system_user: SystemUserModel, test_emulation: EmulationModel) -> EmulationRunModel:
    with create_test_session() as session:
        emulation_run = db.EmulationRun(
            emulation_id=test_emulation.id,
            initiated_by=service_system_user.login,
            port=5000,
            status=db.EmulationStatus.CREATED,
        )
        session.add(emulation_run)
        session.flush()
        return EmulationRunModel.from_orm(emulation_run)


@pytest.fixture(scope="module")
def envs_for_mock() -> dict[str, str | None]:
    return {
        "OVERHAVE_EMULATION_BASE_CMD": "overhave emulate",
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture(scope="module")
def emulation_settings(mock_envs: None) -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture()
def test_draft(
    faker: Faker, test_scenario: ScenarioModel, test_created_test_run_id: int, service_system_user: SystemUserModel
) -> DraftModel:
    with create_test_session() as session:
        draft: db.Draft = db.Draft(
            feature_id=test_scenario.feature_id,
            test_run_id=test_created_test_run_id,
            text=test_scenario.text,
            published_by=service_system_user.login,
            status=DraftStatus.CREATED,
        )
        draft.pr_url = faker.word()
        draft.published_at = datetime.now()
        session.add(draft)
        session.flush()
        return cast(DraftModel, DraftModel.from_orm(draft))
