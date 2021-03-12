from unittest import mock

import pytest
from _pytest.fixtures import FixtureRequest
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from faker import Faker

from overhave import db
from overhave.admin.views import TagsView


@pytest.fixture()
def user_role_mock(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def current_user_mock(user_role_mock, faker: Faker) -> mock.MagicMock:
    with mock.patch("overhave.admin.views.tag.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = faker.word()
        mocked.role = user_role_mock
        yield mocked


@pytest.fixture()
def session_mock():
    with UnifiedAlchemyMagicMock() as session:
        tag_view = TagsView(model=db.Tags, session=session.add(db.Tags()))
        yield tag_view
