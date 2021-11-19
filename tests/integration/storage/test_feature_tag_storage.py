import pytest
from faker import Faker

from overhave import db
from overhave.entities import SystemUserModel, TagModel
from overhave.storage import FeatureTagStorage


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
        assert tag_model.id == test_tag.id
        assert tag_model.value == test_tag.value
        assert tag_model.created_by == test_tag.created_by
