import pytest

from overhave.storage import FeatureTypeModel, FeatureTypeStorage


def _check_base_feature_type_model(test_model: FeatureTypeModel, validation_model: FeatureTypeModel) -> None:
    assert test_model.id == validation_model.id
    assert test_model.name == validation_model.name


@pytest.mark.usefixtures("database")
class TestFeatureTypeStorage:
    """Integration tests for :class:`FeatureTypeStorage`."""

    def test_get_default_feature_type(
        self, test_feature_type_storage: FeatureTypeStorage, test_feature_type: FeatureTypeModel
    ) -> None:
        model = test_feature_type_storage.get_default_feature_type()
        assert model is not None
        _check_base_feature_type_model(test_model=model, validation_model=test_feature_type)

    def test_get_exists_feature_type(
        self, test_feature_type_storage: FeatureTypeStorage, test_feature_type: FeatureTypeModel
    ) -> None:
        model = test_feature_type_storage.get_feature_type_by_name(test_feature_type.name)
        assert model is not None
        _check_base_feature_type_model(test_model=model, validation_model=test_feature_type)

    def test_get_all_types_empty(
        self,
        test_feature_type_storage: FeatureTypeStorage,
    ) -> None:
        models = test_feature_type_storage.get_all_feature_types()
        assert not models

    def test_get_all_types(
        self, test_feature_type_storage: FeatureTypeStorage, test_feature_type: FeatureTypeModel
    ) -> None:
        models = test_feature_type_storage.get_all_feature_types()
        assert len(models) == 1
        assert models[0] == test_feature_type
