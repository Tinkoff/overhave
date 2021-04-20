from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave import db
from overhave.db.tables import Tags
from overhave.entities.converters import SystemUserModel


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
def test_tags_factory(test_system_user: SystemUserModel):
    def _test_tags(value: str) -> None:
        with db.create_session() as session:
            tags = Tags(value=value, created_by=test_system_user.login)
            session.add(tags)
            session.flush()

    return _test_tags
