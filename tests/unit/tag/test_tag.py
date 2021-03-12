from unittest import mock

import pytest
from wtforms import ValidationError

from overhave import db


class TestTagView:
    """ Integration tests for Tags. """

    @pytest.mark.parametrize("user_role_mock", [db.Role.admin], indirect=True)
    def test_get_tag_created_by(self, test_tags_view, current_user_mock, test_tags_row):
        test_tags_view.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=True)
        assert test_tags_row.created_by == current_user_mock.login

    @pytest.mark.parametrize("user_role_mock", [db.Role.admin], indirect=True)
    def test_get_tag_created_not_change(self, test_tags_view, current_user_mock, test_tags_row):
        test_tags_view.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=False)
        assert test_tags_row.created_by is None

    @pytest.mark.parametrize("user_role_mock", [db.Role.user], indirect=True)
    def test_get_tag_created_error(self, test_tags_view, current_user_mock, test_tags_row):
        with pytest.raises(ValidationError):
            test_tags_view.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=False)

    @pytest.mark.parametrize("user_role_mock", [db.Role.user], indirect=True)
    def test_get_tag_delete_error(self, test_tags_view, current_user_mock, test_tags_row):
        with pytest.raises(ValidationError):
            test_tags_view.on_model_delete(model=test_tags_row)
