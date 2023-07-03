from copy import deepcopy
from unittest import mock

import pytest
from faker import Faker
from wtforms import ValidationError

from overhave import db
from overhave.admin import views


@pytest.mark.parametrize("test_mock_patch_user_directory", ["overhave.admin.views.tag.current_user"], indirect=True)
class TestTagView:
    """Unit tests for TagsView."""

    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_get_tag_created_not_change(
        self,
        test_tags_view: views.TagsView,
        current_user_mock: mock.MagicMock,
        test_tags_row: db.Tags,
        form_mock: mock.MagicMock,
    ) -> None:
        previous_row = deepcopy(test_tags_row)
        test_tags_view.on_model_change(form=form_mock, model=test_tags_row, is_created=False)
        assert test_tags_row.id == previous_row.id
        assert test_tags_row.value == previous_row.value
        assert test_tags_row.created_by == previous_row.created_by

    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_get_tag_validation_error_tag_not_creator_or_admin(
        self,
        test_tags_view: views.TagsView,
        current_user_mock: mock.MagicMock,
        test_tags_row: db.Tags,
        form_mock: mock.MagicMock,
    ) -> None:
        with pytest.raises(ValidationError):
            test_tags_view.on_model_change(form=form_mock, model=test_tags_row, is_created=False)

    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_get_tag_delete_error(
        self, test_tags_view: views.TagsView, current_user_mock: mock.MagicMock, test_tags_row: db.Tags
    ) -> None:
        with pytest.raises(ValidationError):
            test_tags_view.on_model_delete(model=test_tags_row)

    @pytest.mark.parametrize("user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_tag_created_by(
        self,
        test_tags_view: views.TagsView,
        current_user_mock: mock.MagicMock,
        test_tags_row: db.Tags,
        faker: Faker,
        form_mock: mock.MagicMock,
    ) -> None:
        form_mock.data["value"] = faker.word()
        test_tags_view.on_model_change(form=form_mock, model=test_tags_row, is_created=True)
        assert test_tags_row.created_by == current_user_mock.login

    @pytest.mark.parametrize("user_role", [db.Role.admin, db.Role.user], indirect=True)
    @pytest.mark.parametrize("value", ["(!)", "+5", "k$ek", "@", "(*"])
    def test_incorrect_tag_raises_error(
        self,
        test_tags_view: views.TagsView,
        current_user_mock: mock.MagicMock,
        test_tags_row: db.Tags,
        faker: Faker,
        form_mock: mock.MagicMock,
        value: str,
    ) -> None:
        form_mock.data["value"] = value
        with pytest.raises(ValidationError):
            test_tags_view.on_model_change(form=form_mock, model=test_tags_row, is_created=True)
