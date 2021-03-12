from unittest import mock

import pytest
from wtforms import ValidationError

from overhave import db


class TestTagView:
    """ Integration tests for Tags. """

    @pytest.mark.parametrize("user_role_mock", ["admin"], indirect=True)
    def test_get_tag_created_by(self, session_mock, current_user_mock):
        db_tags = db.Tags()
        session_mock.on_model_change(form=mock.MagicMock(), model=db_tags, is_created=True)
        assert db_tags.created_by

    @pytest.mark.parametrize("user_role_mock", ["admin"], indirect=True)
    def test_get_tag_created_not_change(
        self, session_mock, current_user_mock,
    ):
        db_tags = db.Tags()
        session_mock.on_model_change(form=mock.MagicMock(), model=db_tags, is_created=False)
        assert db_tags.created_by is None

    def test_get_tag_created_error(self, session_mock, current_user_mock):
        db_tags = db.Tags()
        with pytest.raises(ValidationError):
            session_mock.on_model_change(form=mock.MagicMock(), model=db_tags, is_created=False)

    def test_get_tag_delete_error(self, session_mock, current_user_mock):
        db_tags = db.Tags()
        with pytest.raises(ValidationError):
            session_mock.on_model_delete(model=db_tags)
