from typing import Optional

import pytest
from faker import Faker

from overhave import db
from overhave.entities import SystemUserModel, TagModel
from overhave.storage import FeatureTagStorage


def _validate_tag_model(tag: Optional[TagModel], validation_tag: TagModel) -> None:
    assert tag is not None
    assert tag.id == validation_tag.id
    assert tag.value == validation_tag.value
    assert tag.created_by == validation_tag.created_by


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
class TestFeatureTagStorage:
    """Integration tests for :class:`FeatureTagStorage`."""

    def test_create_tag(
        self, test_tag_storage: FeatureTagStorage, test_system_user: SystemUserModel, faker: Faker
    ) -> None:
        tag_value = faker.word()
        tag_model = test_tag_storage.get_or_create_tag(value=tag_value, created_by=test_system_user.login)
        assert tag_model.value == tag_value
        assert tag_model.created_by == test_system_user.login

    def test_get_tag(self, test_tag_storage: FeatureTagStorage, test_tag: TagModel) -> None:
        tag_model = test_tag_storage.get_or_create_tag(value=test_tag.value, created_by=test_tag.created_by)
        _validate_tag_model(tag=tag_model, validation_tag=test_tag)

    def test_get_tag_by_value_not_exist(
        self, test_tag_storage: FeatureTagStorage, faker: Faker, test_user_role: db.Role
    ) -> None:
        tag_model = test_tag_storage.get_tag_by_value(faker.word())
        assert tag_model is None

    def test_get_tag_by_value(self, test_tag_storage: FeatureTagStorage, test_tag: TagModel) -> None:
        tag_model = test_tag_storage.get_tag_by_value(test_tag.value)
        _validate_tag_model(tag=tag_model, validation_tag=test_tag)

    def test_get_tags_like_value(self, test_tag_storage: FeatureTagStorage, test_tag: TagModel) -> None:
        tag_models = test_tag_storage.get_tags_like_value(test_tag.value)
        assert len(tag_models) == 1
        _validate_tag_model(tag=tag_models[0], validation_tag=test_tag)
