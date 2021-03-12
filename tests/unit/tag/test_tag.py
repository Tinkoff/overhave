from unittest import mock

import pytest
from wtforms import ValidationError

from overhave import db


class TestTagView:
    """ Integration tests for Tags. """

    @pytest.mark.parametrize("user_role_mock", [db.Role.admin], indirect=True)
    def test_get_tag_created_by(self, session_mock, current_user_mock, test_tags_row):
        session_mock.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=True)
        assert test_tags_row.created_by

    @pytest.mark.parametrize("user_role_mock", [db.Role.admin], indirect=True)
    def test_get_tag_created_not_change(self, session_mock, current_user_mock, test_tags_row):
        session_mock.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=False)
        assert test_tags_row.created_by is None

    @pytest.mark.parametrize("user_role_mock", [db.Role.user], indirect=True)
    def test_get_tag_created_error(self, session_mock, current_user_mock, test_tags_row):
        with pytest.raises(ValidationError):
            session_mock.on_model_change(form=mock.MagicMock(), model=test_tags_row, is_created=False)

    @pytest.mark.parametrize("user_role_mock", [db.Role.user], indirect=True)
    def test_get_tag_delete_error(self, session_mock, current_user_mock, test_tags_row):
        with pytest.raises(ValidationError):
            session_mock.on_model_delete(model=test_tags_row)
