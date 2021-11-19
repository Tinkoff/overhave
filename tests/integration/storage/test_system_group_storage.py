import pytest
from faker import Faker

from overhave import db
from overhave.storage import SystemUserGroupStorage


@pytest.mark.usefixtures("database")
class TestSystemGroupStorage:
    """Integration tests for :class:`TestSystemGroupStorage`."""

    def test_has_any_group_true(self, test_system_user_group_storage: SystemUserGroupStorage, faker: Faker) -> None:
        group = faker.word()
        with db.create_session() as session:
            session.add(db.GroupRole(group=group))
        assert test_system_user_group_storage.has_any_group([group])

    def test_has_any_group_false(self, test_system_user_group_storage: SystemUserGroupStorage, faker: Faker) -> None:
        assert not test_system_user_group_storage.has_any_group([faker.word()])
