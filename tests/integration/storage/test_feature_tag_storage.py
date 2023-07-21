import pytest
from faker import Faker

from overhave import db
from overhave.storage import FeatureTagStorage, SystemUserModel, TagModel
from tests.db_utils import count_queries


def _validate_tag_model(tag: TagModel | None, validation_tag: TagModel) -> None:
    assert tag is not None
    assert tag.id == validation_tag.id
    assert tag.value == validation_tag.value
    assert tag.created_by == validation_tag.created_by


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
class TestFeatureTagStorage:
    """Integration tests for :class:`FeatureTagStorage`."""

    def test_create_tag(
        self, test_tag_storage: FeatureTagStorage, service_system_user: SystemUserModel, faker: Faker
    ) -> None:
        tag_value = faker.word()
        with count_queries(2):
            with db.create_session() as session:
                db_tag = test_tag_storage.get_or_create_tag(
                    session=session, value=tag_value, created_by=service_system_user.login
                )
                session.flush()
                assert db_tag.value == tag_value
                assert db_tag.created_by == service_system_user.login

    def test_get_tag(self, test_tag_storage: FeatureTagStorage, test_tag: TagModel) -> None:
        with count_queries(1):
            with db.create_session() as session:
                db_tag = test_tag_storage.get_or_create_tag(
                    session=session, value=test_tag.value, created_by=test_tag.created_by
                )
                session.flush()
                tag_model = TagModel.model_validate(db_tag)
        _validate_tag_model(tag=tag_model, validation_tag=test_tag)

    def test_get_tag_by_value_not_exist(
        self, test_tag_storage: FeatureTagStorage, faker: Faker, test_user_role: db.Role
    ) -> None:
        with count_queries(1):
            tag_model = test_tag_storage.get_tag_by_value(faker.word())
        assert tag_model is None

    def test_get_tag_by_value(self, test_tag_storage: FeatureTagStorage, test_tag: TagModel) -> None:
        with count_queries(1):
            tag_model = test_tag_storage.get_tag_by_value(test_tag.value)
        _validate_tag_model(tag=tag_model, validation_tag=test_tag)

    def test_get_tags_like_value(self, test_tag_storage: FeatureTagStorage, test_tag: TagModel) -> None:
        with count_queries(1):
            tag_models = test_tag_storage.get_tags_like_value(test_tag.value)
        assert len(tag_models) == 1
        _validate_tag_model(tag=tag_models[0], validation_tag=test_tag)
