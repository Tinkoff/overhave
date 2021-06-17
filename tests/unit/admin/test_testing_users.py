from unittest import mock

import pytest
from faker import Faker
from wtforms.validators import ValidationError

from overhave import db
from overhave.admin.views.testing_users import TestUserView


class TestTestingUsers:
    """ Unit tests for View. """

    @pytest.mark.parametrize(
        "test_mock_patch_user_directory", ["overhave.admin.views.testing_users.current_user"], indirect=True
    )
    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_admin_delete_testing_users(
        self,
        test_testing_user_view: TestUserView,
        test_testing_user_row: db.TestUser,
        current_user_mock: mock.MagicMock,
    ) -> None:
        test_testing_user_view.on_model_delete(model=test_testing_user_row)

    @pytest.mark.parametrize(
        "test_mock_patch_user_directory", ["overhave.admin.views.testing_users.current_user"], indirect=True
    )
    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_user_doesnt_delete_testing_users(
        self,
        test_testing_user_view: TestUserView,
        test_testing_user_row: db.TestUser,
        current_user_mock: mock.MagicMock,
    ) -> None:
        with pytest.raises(ValidationError):
            test_testing_user_view.on_model_delete(model=test_testing_user_row)

    @pytest.mark.parametrize(
        "test_mock_patch_user_directory", ["overhave.admin.views.testing_users.current_user"], indirect=True
    )
    @pytest.mark.parametrize("user_role", [db.Role.user, db.Role.admin], indirect=True)
    @pytest.mark.parametrize("test_is_created", [False, True])
    def test_incorrect_model_raises_error(
        self,
        test_testing_user_view: TestUserView,
        test_incorrect_testing_user_row: db.TestUser,
        current_user_mock: mock.MagicMock,
        form_mock: mock.MagicMock,
        test_is_created: bool,
    ) -> None:
        with pytest.raises(ValidationError):
            test_testing_user_view.on_model_change(
                form=form_mock, model=test_incorrect_testing_user_row, is_created=test_is_created
            )

    @pytest.mark.parametrize(
        "test_mock_patch_user_directory", ["overhave.admin.views.testing_users.current_user"], indirect=True
    )
    @pytest.mark.parametrize("user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_on_form_prefill(
        self,
        test_testing_user_view: TestUserView,
        current_user_mock: mock.MagicMock,
        form_mock: mock.MagicMock,
        faker: Faker,
    ) -> None:
        assert test_testing_user_view._feature_type is None
        test_testing_user_view.on_form_prefill(form=form_mock, id=faker.word())
        assert test_testing_user_view._feature_type is not None
