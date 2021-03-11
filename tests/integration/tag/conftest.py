from unittest import mock

import pytest

from overhave import db


@pytest.fixture()
def current_admin_user_mock() -> mock.MagicMock:
    with mock.patch("overhave.admin.views.tag.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = "test_admin_user"
        mocked.role = db.Role.admin
        yield mocked


@pytest.fixture()
def current_user_mock() -> mock.MagicMock:
    with mock.patch("overhave.admin.views.tag.current_user", return_value=mock.MagicMock()) as mocked:
        mocked.login = "test_user"
        mocked.role = db.Role.user
        yield mocked
