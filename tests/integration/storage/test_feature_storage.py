from uuid import uuid1

import pytest

from overhave import db
from overhave.entities import FeatureModel, FeatureTypeModel
from overhave.storage import FeatureStorage


def _check_base_feature_attrs(test_model: FeatureModel, validation_model: FeatureModel) -> None:
    assert test_model.name == validation_model.name
    assert test_model.author == validation_model.author
    assert test_model.type_id == validation_model.type_id
    assert test_model.file_path == validation_model.file_path
    assert test_model.task == validation_model.task
    assert test_model.last_edited_by == validation_model.last_edited_by
    assert test_model.released == validation_model.released


def _check_base_feature_type_attrs(test_model: FeatureTypeModel, validation_model: FeatureTypeModel) -> None:
    assert test_model is not None
    assert test_model.id == validation_model.id
    assert test_model.name == validation_model.name


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
        _check_base_feature_attrs(test_model=feature_model, validation_model=test_feature)
        _check_base_feature_type_attrs(test_model=feature_model.feature_type, validation_model=test_feature_type)

    def test_create_feature(
        self, test_feature_storage: FeatureStorage, test_feature_type: FeatureTypeModel, test_feature: FeatureModel
    ) -> None:
        test_feature.name = uuid1().hex
        test_feature.file_path = uuid1().hex
        with db.create_session() as session:
            feature_id = test_feature_storage.create_feature(session=session, model=test_feature)
        feature_model = test_feature_storage.get_feature(feature_id)
        assert feature_model is not None
        assert feature_model.id == feature_id
        _check_base_feature_attrs(test_model=feature_model, validation_model=test_feature)
        _check_base_feature_type_attrs(test_model=feature_model.feature_type, validation_model=test_feature_type)
