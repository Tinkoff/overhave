from unittest import mock

import pytest

from overhave import db

user = "test_user"


@pytest.fixture()
def db_create_user() -> None:
    with db.create_session() as session:
        session.add(db.UserRole(login=user, password="12345", role=db.Role.admin))


@pytest.fixture()
def db_create_tag() -> None:
    with db.create_session() as session:
        session.add(db.Tags(value="TestTagName", created_by=user))


@pytest.fixture()
def is_accessible_mock() -> mock.MagicMock:
    with mock.patch(
        "overhave.admin.views.base.ModelViewConfigured.is_accessible", return_value=mock.MagicMock()
    ) as mocked:
        mocked.return_value = True
        yield mocked


@pytest.fixture()
def current_user_mock() -> mock.MagicMock:
    with mock.patch("overhave.admin.views.tag.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = user
        mocked.role = db.Role.admin
        yield mocked
