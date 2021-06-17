from unittest import mock

import pytest
from faker import Faker
from wtforms.validators import ValidationError

from overhave import db
from overhave.admin.views import FeatureView


@pytest.mark.parametrize("test_mock_patch_user_directory", ["overhave.admin.views.feature.current_user"], indirect=True)
class TestFeatueView:
    """ Unit tests for FeatureView. """

    @pytest.mark.parametrize("test_feature_model_task", [Faker().word()])
    @pytest.mark.parametrize("user_role", [db.Role.admin], indirect=True)
    def test_delete_feature_correctly(
        self, test_feature_view: FeatureView, current_user_mock: mock.MagicMock, test_feature_row: db.Feature,
    ) -> None:
        test_feature_view.on_model_delete(model=test_feature_row)

    @pytest.mark.parametrize("test_feature_model_task", [Faker().word()])
    @pytest.mark.parametrize("user_role", [db.Role.user], indirect=True)
    def test_delete_feature_incorrect(
        self, test_feature_view: FeatureView, current_user_mock: mock.MagicMock, test_feature_row: db.Feature,
    ) -> None:
        with pytest.raises(ValidationError):
            test_feature_view.on_model_delete(model=test_feature_row)
