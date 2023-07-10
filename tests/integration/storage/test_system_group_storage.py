import pytest
from faker import Faker

from overhave import db
from overhave.storage import SystemUserGroupStorage
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
class TestSystemGroupStorage:
    """Integration tests for :class:`TestSystemGroupStorage`."""

    def test_has_any_group_true(self, test_system_user_group_storage: SystemUserGroupStorage, faker: Faker) -> None:
        group = faker.word()
        with create_test_session() as session:
            session.add(db.GroupRole(group=group))
        with count_queries(1):
            with db.create_session() as session:
                assert test_system_user_group_storage.has_any_group(session=session, user_groups=[group])

    def test_has_any_group_false(self, test_system_user_group_storage: SystemUserGroupStorage, faker: Faker) -> None:
        with count_queries(1):
            with db.create_session() as session:
                assert not test_system_user_group_storage.has_any_group(session=session, user_groups=[faker.word()])
