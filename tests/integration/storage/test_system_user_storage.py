import pytest
from faker import Faker
from pydantic import SecretStr

from overhave import db
from overhave.storage import SystemUserModel, SystemUserStorage
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
class TestSystemUserStorage:
    """Integration tests for :class:`TestSystemUserStorage`."""

    def test_get_existing_user(
        self, test_system_user_storage: SystemUserStorage, service_system_user: SystemUserModel
    ) -> None:
        with count_queries(1):
            user = test_system_user_storage.get_user_model(service_system_user.id)
        assert user is not None
        assert user == service_system_user

    def test_get_not_existing_user(
        self, test_system_user_storage: SystemUserStorage, service_system_user: SystemUserModel
    ) -> None:
        with count_queries(1):
            user = test_system_user_storage.get_user_model(service_system_user.id + 1)
        assert user is None

    @pytest.mark.parametrize("test_system_user_password", [None, SecretStr("secret password")])
    def test_create_user_with_password(
        self,
        test_system_user_storage: SystemUserStorage,
        test_user_role: db.Role,
        test_system_user_password: SecretStr | None,
        faker: Faker,
    ) -> None:
        login = faker.word()
        with count_queries(1):
            with db.create_session() as session:
                user = test_system_user_storage.create_user(
                    session=session, login=login, password=test_system_user_password, role=test_user_role
                )
                user_id = user.id
        with create_test_session() as session:
            db_user: db.UserRole = session.query(db.UserRole).filter(db.UserRole.id == user_id).one()
            assert db_user.login == login
            if test_system_user_password is None:
                assert db_user.password is None
            else:
                assert db_user.password == test_system_user_password.get_secret_value()
            assert db_user.role is test_user_role

    @pytest.mark.parametrize("test_system_user_password", [None, SecretStr("secret password")])
    def test_get_existing_user_by_credits(
        self,
        test_system_user_storage: SystemUserStorage,
        test_system_user_password: SecretStr | None,
        test_user_role: db.Role,
        faker: Faker,
    ) -> None:
        with create_test_session() as session:
            db_user = test_system_user_storage.create_user(
                session=session, login=faker.word(), password=test_system_user_password, role=test_user_role
            )
            created_user_model = SystemUserModel.model_validate(db_user)
        with count_queries(1):
            with db.create_session() as session:
                gotten_db_user = test_system_user_storage.get_user_by_credits(
                    session=session, login=created_user_model.login, password=created_user_model.password
                )
                assert gotten_db_user is not None
                gotten_user_model = SystemUserModel.model_validate(gotten_db_user)
        assert gotten_user_model == created_user_model

    @pytest.mark.parametrize("test_system_user_password", [None, SecretStr("secret password")])
    def test_get_not_existing_user_by_credits(
        self,
        test_system_user_storage: SystemUserStorage,
        test_system_user_password: SecretStr | None,
        test_user_role: db.Role,
        faker: Faker,
    ) -> None:
        with count_queries(1):
            with db.create_session() as session:
                assert (
                    test_system_user_storage.get_user_by_credits(
                        session=session, login=faker.word(), password=test_system_user_password
                    )
                    is None
                )
