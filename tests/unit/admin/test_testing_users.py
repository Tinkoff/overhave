from unittest import mock

import pytest
from wtforms.validators import ValidationError

from overhave import db
from overhave.admin.views.testing_users import TestUserView


class TestTestingUsers:
    """ Unit tests for View. """

    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_admin_delete_testing_users(
        self,
        test_testing_user_view: TestUserView,
        test_testing_user_row: db.TestUser,
        current_testing_users_user_mock: mock.MagicMock,
    ) -> None:
        test_testing_user_view.on_model_delete(model=test_testing_user_row)

    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_user_doesnt_delete_testing_users(
        self,
        test_testing_user_view: TestUserView,
        test_testing_user_row: db.TestUser,
        current_testing_users_user_mock: mock.MagicMock,
    ) -> None:
        with pytest.raises(ValidationError):
            test_testing_user_view.on_model_delete(model=test_testing_user_row)

    @pytest.mark.parametrize("user_role", [db.Role.user, db.Role.admin], indirect=True)
    def test_incorrect_model_raises_error(
        self,
        test_testing_user_view: TestUserView,
        test_incorrect_testing_user_row: db.TestUser,
        current_testing_users_user_mock: mock.MagicMock,
        form_mock: mock.MagicMock,
    ) -> None:
        with pytest.raises(ValidationError):
            test_testing_user_view.on_model_change(
                form=form_mock, model=test_incorrect_testing_user_row, is_created=True
            )
