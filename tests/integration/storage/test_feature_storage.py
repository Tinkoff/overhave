from typing import cast
from uuid import uuid1

import pytest
from faker import Faker

from overhave import db
from overhave.entities import FeatureModel, FeatureTypeModel, TagModel
from overhave.storage import FeatureStorage, FeatureTagStorage, SystemUserStorage
from overhave.utils import get_current_time


def _check_base_feature_attrs(test_model: FeatureModel, validation_model: FeatureModel) -> None:
    assert test_model.name == validation_model.name
    assert test_model.author == validation_model.author
    assert test_model.type_id == validation_model.type_id
    assert test_model.file_path == validation_model.file_path
    assert test_model.task == validation_model.task
    assert test_model.last_edited_by == validation_model.last_edited_by
    assert test_model.released == validation_model.released
    assert test_model.feature_tags == validation_model.feature_tags


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
        feature_id = test_feature_storage.create_feature(model=test_feature)
        feature_model = test_feature_storage.get_feature(feature_id)
        assert feature_model is not None
        assert feature_model.id == feature_id
        _check_base_feature_attrs(test_model=feature_model, validation_model=test_feature)
        _check_base_feature_type_attrs(test_model=feature_model.feature_type, validation_model=test_feature_type)

    def test_update_feature(
        self,
        test_feature_storage: FeatureStorage,
        test_system_user_storage: SystemUserStorage,
        test_tag_storage: FeatureTagStorage,
        test_feature_type: FeatureTypeModel,
        test_feature_with_tag: FeatureModel,
        faker: Faker,
    ) -> None:
        new_system_user = test_system_user_storage.create_user(login=uuid1().hex)
        with db.create_session() as session:
            new_tag_id = test_tag_storage.get_or_create_tag(
                session, value=faker.word(), created_by=new_system_user.login
            )
            db_new_tag: db.Tags = session.query(db.Tags).filter(db.Tags.id == new_tag_id).one()
            new_tag_model = cast(TagModel, TagModel.from_orm(db_new_tag))
        new_feature_model = FeatureModel(
            id=test_feature_with_tag.id,
            name=uuid1().hex,
            author=test_feature_with_tag.author,
            type_id=test_feature_type.id,
            last_edited_by=new_system_user.login,
            last_edited_at=get_current_time(),
            task=[uuid1().hex],
            file_path=uuid1().hex,
            released=True,
            feature_type=test_feature_type,
            feature_tags=[new_tag_model],
        )
        test_feature_storage.update_feature(model=new_feature_model)
        updated_feature_model = test_feature_storage.get_feature(new_feature_model.id)
        assert updated_feature_model is not None
        assert updated_feature_model.id == new_feature_model.id
        _check_base_feature_attrs(test_model=updated_feature_model, validation_model=new_feature_model)
        _check_base_feature_type_attrs(
            test_model=updated_feature_model.feature_type, validation_model=test_feature_type
        )
