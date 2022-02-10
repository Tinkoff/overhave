import pytest

from overhave import db
from overhave.entities import FeatureTypeModel, SystemUserModel
from overhave.entities.converters import TestUserModel, TestUserSpecification
from overhave.storage.test_user_storage import TestUserStorage


@pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
class TestTestUserStorage:
    """Integration tests for :class:`TestUserStorage`."""

    def test_create_test_user(
        self,
        test_user_storage: TestUserStorage,
        test_user_name: str,
        test_specification: TestUserSpecification,
        test_feature_type: FeatureTypeModel,
        test_system_user: SystemUserModel,
    ) -> None:
        assert test_user_storage.get_test_user_by_name(test_user_name) is None
        test_user_storage.create_test_user(
            name=test_user_name,
            specification=test_specification,
            feature_type=test_feature_type.name,
            created_by=test_system_user.login,
        )
        test_user = test_user_storage.get_test_user_by_name(test_user_name)
        assert test_user is not None
        assert test_user.name == test_user_name
        assert test_user.specification == test_specification

    @pytest.mark.parametrize("new_specification", [{"kek": "lol", "overhave": "test"}, {}, {"test": "new_value"}])
    def test_update_test_user_specification(
        self,
        test_user_storage: TestUserStorage,
        test_testuser: TestUserModel,
        test_specification: TestUserSpecification,
        new_specification: TestUserSpecification,
    ) -> None:
        assert test_testuser.specification == test_specification
        test_user_storage.update_test_user_specification(test_testuser.id, new_specification)
        test_user = test_user_storage.get_test_user_by_name(test_testuser.name)
        assert test_user is not None
        assert test_user.specification == new_specification
