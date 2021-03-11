from unittest import mock

import pytest
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from wtforms import ValidationError

from overhave import db
from overhave.admin.views import TagsView


class TestTagView:
    """ Integration tests for Tags. """

    def test_get_tag_created_by(
        self, current_admin_user_mock,
    ):
        db_tags = db.Tags()
        with UnifiedAlchemyMagicMock() as session:
            tag_view = TagsView(model=db.Tags, session=session.add(db.Tags()))
            tag_view.on_model_change(form=mock.MagicMock(), model=db_tags, is_created=True)
        assert db_tags.created_by == "test_admin_user"

    def test_get_tag_created_not_change(
        self, current_admin_user_mock,
    ):
        db_tags = db.Tags()
        with UnifiedAlchemyMagicMock() as session:
            tag_view = TagsView(model=db.Tags, session=session.add(db.Tags()))
            tag_view.on_model_change(form=mock.MagicMock(), model=db_tags, is_created=False)
        assert db_tags.created_by is None

    def test_get_tag_created_error(
        self, current_user_mock,
    ):
        db_tags = db.Tags()
        with UnifiedAlchemyMagicMock() as session:
            tag_view = TagsView(model=db.Tags, session=session.add(db.Tags()))
            with pytest.raises(ValidationError):
                tag_view.on_model_change(form=mock.MagicMock(), model=db_tags, is_created=False)

    def test_get_tag_delete_error(
        self, current_user_mock,
    ):
        db_tags = db.Tags()
        with UnifiedAlchemyMagicMock() as session:
            tag_view = TagsView(model=db.Tags, session=session.add(db.Tags()))
            with pytest.raises(ValidationError):
                tag_view.on_model_delete(model=db_tags)
