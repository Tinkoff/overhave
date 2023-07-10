from uuid import uuid1

import allure
import pytest
from faker import Faker

from overhave import db
from overhave.storage import (
    FeatureModel,
    FeatureStorage,
    FeatureTagStorage,
    FeatureTypeModel,
    SystemUserStorage,
    TagModel,
)
from overhave.utils import get_current_time
from tests.db_utils import count_queries, create_test_session


def _check_base_feature_attrs(test_model: FeatureModel | db.Feature, validation_model: FeatureModel) -> None:
    assert test_model.name == validation_model.name
    assert test_model.author == validation_model.author
    assert test_model.type_id == validation_model.type_id
    assert test_model.file_path == validation_model.file_path
    assert test_model.task == validation_model.task
    assert test_model.last_edited_by == validation_model.last_edited_by
    assert test_model.released == validation_model.released
    assert test_model.feature_tags == validation_model.feature_tags
    assert test_model.severity == validation_model.severity


def _check_base_feature_type_attrs(
    test_model: FeatureTypeModel | db.FeatureType, validation_model: FeatureTypeModel
) -> None:
    assert test_model is not None
    assert test_model.id == validation_model.id
    assert test_model.name == validation_model.name


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
@pytest.mark.parametrize("test_severity", list(allure.severity_level), indirect=True)
class TestFeatureStorage:
    """Integration tests for :class:`FeatureStorage`."""

    def test_feature_model_by_id(
        self, test_feature_storage: FeatureStorage, test_feature_type: FeatureTypeModel, test_feature: FeatureModel
    ) -> None:
        with count_queries(3):
            with db.create_session() as session:
                feature_model = test_feature_storage.feature_model_by_id(session=session, feature_id=test_feature.id)
        assert feature_model is not None
        assert feature_model.id == test_feature.id
        _check_base_feature_attrs(test_model=feature_model, validation_model=test_feature)
        _check_base_feature_type_attrs(test_model=feature_model.feature_type, validation_model=test_feature_type)

    def test_create_feature(
        self, test_feature_storage: FeatureStorage, test_feature_type: FeatureTypeModel, test_feature: FeatureModel
    ) -> None:
        test_feature.name = uuid1().hex
        test_feature.file_path = uuid1().hex
        with count_queries(1):
            feature_id = test_feature_storage.create_feature(model=test_feature)
        with create_test_session() as session:
            feature = session.get(db.Feature, feature_id)
            assert feature is not None
            assert feature.id == feature_id
            _check_base_feature_attrs(test_model=feature, validation_model=test_feature)
            _check_base_feature_type_attrs(test_model=feature.feature_type, validation_model=test_feature_type)

    @pytest.mark.parametrize("updated_severity", list(allure.severity_level))
    def test_update_feature(
        self,
        test_feature_storage: FeatureStorage,
        test_system_user_storage: SystemUserStorage,
        test_tag_storage: FeatureTagStorage,
        test_feature_type: FeatureTypeModel,
        test_feature_with_tag: FeatureModel,
        updated_severity: allure.severity_level,
        faker: Faker,
    ) -> None:
        system_user_login = f"{faker.word()}_{faker.word()}"
        with create_test_session() as session:
            test_system_user_storage.create_user(session=session, login=system_user_login)
            new_db_tag = db.Tags(value=faker.word() + faker.word(), created_by=system_user_login)
            session.add(new_db_tag)
            session.flush()
            new_tag_model = TagModel.from_orm(new_db_tag)

        new_feature_model = FeatureModel(
            id=test_feature_with_tag.id,
            created_at=get_current_time(),
            name=uuid1().hex,
            author=test_feature_with_tag.author,
            type_id=test_feature_type.id,
            last_edited_by=system_user_login,
            last_edited_at=get_current_time(),
            task=[uuid1().hex],
            file_path=uuid1().hex,
            released=True,
            feature_type=test_feature_type,
            feature_tags=[new_tag_model],
            severity=updated_severity,
        )
        with count_queries(6):
            test_feature_storage.update_feature(model=new_feature_model)
        with create_test_session() as session:
            updated_feature = test_feature_storage.feature_model_by_id(session=session, feature_id=new_feature_model.id)
        assert updated_feature.id == new_feature_model.id
        _check_base_feature_attrs(test_model=updated_feature, validation_model=new_feature_model)
        _check_base_feature_type_attrs(test_model=updated_feature.feature_type, validation_model=test_feature_type)
        with count_queries(3):
            test_feature_storage.get_features_by_tag(new_tag_model.id)

    def test_get_feature_by_tag(
        self,
        test_feature_storage: FeatureStorage,
        test_tag: TagModel,
        test_feature_with_tag: FeatureModel,
        faker: Faker,
    ) -> None:
        with count_queries(3):
            found_features = test_feature_storage.get_features_by_tag(test_tag.id)
        assert len(found_features) == 1
        assert found_features[0] == test_feature_with_tag
