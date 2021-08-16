from unittest import mock

import pytest
from wtforms.validators import ValidationError

from overhave import db
from overhave.admin.views import DraftView


@pytest.mark.parametrize("test_mock_patch_user_directory", ["overhave.admin.views.draft.current_user"], indirect=True)
class TestDraftView:
    """ Unit tests for DraftView. """

    @pytest.mark.parametrize("test_feature_model_task", [["KEK-1111"]])
    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_admin_can_delete(
        self, test_not_mocked_draft_view: DraftView, test_draft_row: db.Draft, current_user_mock: mock.MagicMock
    ):
        test_not_mocked_draft_view.on_model_delete(test_draft_row)

    @pytest.mark.parametrize("test_feature_model_task", [["KEK-1111"]])
    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_user_cannot_delete(
        self, test_not_mocked_draft_view: DraftView, test_draft_row: db.Draft, current_user_mock: mock.MagicMock
    ):
        with pytest.raises(ValidationError):
            test_not_mocked_draft_view.on_model_delete(test_draft_row)
