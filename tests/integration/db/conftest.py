from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave import db
from overhave.db.tables import Tags
from overhave.entities.converters import SystemUserModel, TagsTypeModel


@pytest.fixture()
def test_user_role(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_system_user(database: None, faker: Faker, test_user_role: db.Role) -> SystemUserModel:
    with db.create_session() as session:
        app_user = db.UserRole(login=faker.word(), password=faker.word(), role=test_user_role)
        session.add(app_user)
        session.flush()
        return cast(SystemUserModel, SystemUserModel.from_orm(app_user))


@pytest.fixture()
def test_tags_with_spaces(faker: Faker, test_system_user: SystemUserModel):
    def _test_tags_with_spaces() -> TagsTypeModel:
        with db.create_session() as session:
            tags = Tags(value="kek ", created_by=test_system_user.login)
            session.add(tags)
            session.flush()
            return cast(TagsTypeModel, tags)

    return _test_tags_with_spaces


@pytest.fixture()
def test_tags_with_special_symbols(faker: Faker, test_system_user: SystemUserModel):
    def _test_tags_with_special_symbols() -> TagsTypeModel:
        with db.create_session() as session:
            tags = Tags(value="kek#!", created_by=test_system_user.login)
            session.add(tags)
            session.flush()
            return cast(TagsTypeModel, tags)

    return _test_tags_with_special_symbols


@pytest.fixture()
def test_correct_tags(faker: Faker, test_system_user: SystemUserModel):
    def _test_correct_tags() -> TagsTypeModel:
        with db.create_session() as session:
            tags = Tags(value=faker.word(), created_by=test_system_user.login)
            session.add(tags)
            session.flush()
            return cast(TagsTypeModel, tags)

    return _test_correct_tags
