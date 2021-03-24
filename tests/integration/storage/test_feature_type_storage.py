import pytest

from overhave.entities import FeatureTypeModel
from overhave.storage import FeatureTypeStorage


@pytest.mark.usefixtures("database")
class TestFeatureTypeStorage:
    """ Integration tests for :class:`FeatureTypeStorage`. """

    def test_get_default_feature_type(
        self, test_feature_type_storage: FeatureTypeStorage, test_feature_type: FeatureTypeModel
    ):
        feature_type_model = test_feature_type_storage.get_default_feature_type()
        assert feature_type_model is not None
        assert feature_type_model.name == test_feature_type.name
