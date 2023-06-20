from typing import cast
from uuid import uuid1

import allure
import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from pydantic import SecretStr

from overhave import OverhaveEmulationSettings, db
from overhave.storage import (
    EmulationModel,
    EmulationRunModel,
    EmulationStorage,
    FeatureModel,
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


@pytest.fixture(scope="module")
def test_emulation_storage() -> EmulationStorage:
    return EmulationStorage(OverhaveEmulationSettings())


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
def test_system_user(
    test_system_user_storage: SystemUserStorage, database: None, faker: Faker, test_user_role: db.Role
) -> SystemUserModel:
    with create_test_session():
        return test_system_user_storage.create_user(
            login=faker.word(), password=SecretStr(faker.word()), role=test_user_role
        )


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
    test_system_user: SystemUserModel,
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
            created_by=test_system_user.login,
            specification=test_specification,
            allow_update=testuser_allow_update,
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_tag(test_system_user: SystemUserModel, faker: Faker) -> TagModel:
    with create_test_session() as session:
        tag = db.Tags(value=faker.word(), created_by=test_system_user.login)
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
    test_system_user: SystemUserModel,
    test_feature_type: FeatureTypeModel,
    test_severity: allure.severity_level,
    faker: Faker,
) -> FeatureModel:
    with create_test_session() as session:
        feature = db.Feature(
            name=faker.word(),
            author=test_system_user.login,
            type_id=test_feature_type.id,
            task=[faker.word()[:11]],
            file_path=f"{faker.word()}/{faker.word()}",
            severity=test_severity,
            last_edited_at=get_current_time(),
            last_edited_by=test_system_user.login,
        )
        session.add(feature)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_features(
    test_system_user: SystemUserModel,
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
                author=test_system_user.login,
                type_id=test_feature_type.id,
                task=[faker.word()[:11]],
                file_path=f"{faker.word()}/{faker.word()}",
                severity=test_severity,
                last_edited_at=get_current_time(),
                last_edited_by=test_system_user.login,
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
def test_emulation(test_system_user: SystemUserModel, test_testuser, faker: Faker) -> EmulationModel:
    with create_test_session() as session:
        emulation = db.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=test_testuser.id,
            created_by=test_system_user.login,
        )
        session.add(emulation)
        session.flush()
        return cast(EmulationModel, EmulationModel.from_orm(emulation))


@pytest.fixture()
def test_emulation_run(test_system_user: SystemUserModel, test_emulation: EmulationModel) -> EmulationRunModel:
    with create_test_session() as session:
        emulation_run = db.EmulationRun(emulation_id=test_emulation.id, initiated_by=test_system_user.login)
        session.add(emulation_run)
        session.flush()
        return EmulationRunModel.from_orm(emulation_run)
