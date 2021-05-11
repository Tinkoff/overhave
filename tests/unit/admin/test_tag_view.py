from unittest import mock

import pytest
from faker import Faker
from wtforms import ValidationError

from overhave import db
from overhave.admin import views


class TestTagView:
    """ Unit tests for TagsView. """

    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_get_tag_created_by(
        self, test_tags_view: views.TagsView, current_user_mock: mock.MagicMock, test_tags_row: db.Tags, faker: Faker) -> None:
        form_mock = mock.MagicMock()
        form_mock["value"] = faker.word()
        test_tags_view.on_model_change(form=form_mock, model=test_tags_row, is_created=True)
        assert test_tags_row.created_by == current_user_mock.login

    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_get_tag_created_not_change(
        self, test_tags_view: views.TagsView, current_user_mock: mock.MagicMock, test_tags_row: db.Tags
    ) -> None:
        test_tags_view.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=False)
        assert test_tags_row.created_by is None

    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_get_tag_created_error(
        self, test_tags_view: views.TagsView, current_user_mock: mock.MagicMock, test_tags_row: db.Tags
    ) -> None:
        with pytest.raises(ValidationError):
            test_tags_view.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=False)

    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_get_tag_delete_error(
        self, test_tags_view: views.TagsView, current_user_mock: mock.MagicMock, test_tags_row: db.Tags
    ) -> None:
        with pytest.raises(ValidationError):
            test_tags_view.on_model_delete(model=test_tags_row)

    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_incorrect_tag_raises_error(
        self, test_tags_view: views.TagsView, current_user_mock: mock.MagicMock, test_tags_row: db.Tags
    ) -> None:
        form_mock = mock.MagicMock()
        form_mock["value"] = "лол!?*;%*№%"
        with pytest.raises(ValidationError):
            test_tags_view.on_model_change(form=form_mock, model=test_tags_row, is_created=True)
