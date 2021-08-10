import pytest

from overhave import db
from overhave.entities import FeatureModel, FeatureTypeModel
from overhave.storage import FeatureStorage


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
class TestFeatureStorage:
    """ Integration tests for :class:`FeatureStorage`. """

    def test_get_feature(
        self, test_feature_storage: FeatureStorage, test_feature_type: FeatureTypeModel, test_feature: FeatureModel
    ) -> None:
        feature_model = test_feature_storage.get_feature(test_feature.id)
        assert feature_model is not None
        assert feature_model.id == test_feature.id
        assert feature_model.name == test_feature.name
        assert feature_model.author == test_feature.author
        assert feature_model.type_id == test_feature.type_id
        assert feature_model.file_path == test_feature.file_path
        assert feature_model.task == test_feature.task
        assert feature_model.last_edited_by == test_feature.last_edited_by
        assert feature_model.released == test_feature.released
        assert feature_model.feature_type is not None
        assert feature_model.feature_type.id == test_feature_type.id
        assert feature_model.feature_type.name == test_feature_type.name
