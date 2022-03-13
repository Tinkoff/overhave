from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from pydantic import SecretStr

from overhave import db
from overhave.entities import FeatureTypeModel, SystemUserModel, TestUserSpecification
from overhave.entities.converters import TagModel, TestUserModel
from overhave.storage import SystemUserGroupStorage, SystemUserStorage, TestUserStorage


@pytest.fixture(scope="package")
def test_system_user_storage() -> SystemUserStorage:
    return SystemUserStorage()


@pytest.fixture(scope="package")
def test_system_user_group_storage() -> SystemUserGroupStorage:
    return SystemUserGroupStorage()


@pytest.fixture(scope="package")
def test_user_storage() -> TestUserStorage:
    return TestUserStorage()


@pytest.fixture()
def test_feature_type(database: None, faker: Faker) -> FeatureTypeModel:
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
def test_system_user(
    test_system_user_storage: SystemUserStorage, database: None, faker: Faker, test_user_role: db.Role
) -> SystemUserModel:
    return test_system_user_storage.create_user(
        login=faker.word(), password=SecretStr(faker.word()), role=test_user_role
    )


@pytest.fixture()
def test_specification() -> TestUserSpecification:
    return TestUserSpecification({"test": "value"})


@pytest.fixture()
def test_testuser(
    test_system_user: SystemUserModel, faker: Faker, test_feature_type, test_specification: TestUserSpecification
) -> TestUserModel:
    with db.create_session() as session:
        test_user = db.TestUser(
            feature_type_id=test_feature_type.id,
            name=cast(str, faker.word()),
            created_by=test_system_user.login,
            specification=test_specification,
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_tag(test_system_user: SystemUserModel, faker: Faker) -> TagModel:
    with db.create_session() as session:
        tag = db.Tags(value=faker.word(), created_by=test_system_user.login)
        session.add(tag)
        session.flush()
        return cast(TagModel, TagModel.from_orm(tag))
