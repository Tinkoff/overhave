from typing import Sequence
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from overhave import db
from overhave.entities import (
    DefaultAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    SimpleAdminAuthorizationManager,
)
from overhave.storage import SystemUserStorage
from tests.db_utils import count_queries, create_test_session


def _create_user_groups(db_groups: Sequence[str]) -> None:
    with create_test_session() as session:
        for group in db_groups:
            session.add(db.GroupRole(group=group))


@pytest.mark.usefixtures("database")
class TestLdapAuthManager:
    """Integration tests for :class:`LDAPAdminAuthorizationManager`."""

    def test_authorize_user_no_groups(
        self,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        mocked_ldap_authenticator.get_user_groups.return_value = []
        assert test_ldap_auth_manager.authorize_user(username=test_username, password=test_password) is None

    def test_authorize_user_no_user_no_groups(
        self,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        mocked_ldap_authenticator.get_user_groups.return_value = ["not_supplied_group"]
        with count_queries(2):
            assert test_ldap_auth_manager.authorize_user(username=test_username, password=test_password) is None

    def test_authorize_user_no_user_has_group(
        self,
        test_db_groups: Sequence[str],
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        mocked_ldap_authenticator.get_user_groups.return_value = test_db_groups
        _create_user_groups(test_db_groups)
        with count_queries(3):
            user = test_ldap_auth_manager.authorize_user(username=test_username, password=test_password)
        assert user is not None
        assert user.login == test_username
        assert user.password is None  # LDAP auth does not require password
        assert user.role is db.Role.user

    @pytest.mark.xfail()
    def test_authorize_user_no_user_admin_group(
        self,
        test_admin_group: str,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_db_groups: list[str],
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        db_groups = [test_admin_group] + test_db_groups
        mocked_ldap_authenticator.get_user_groups.return_value = db_groups
        _create_user_groups(db_groups)
        with count_queries(3):
            user = test_ldap_auth_manager.authorize_user(username=test_username, password=test_password)
        assert user is not None
        assert user.login == test_username
        assert user.password is None  # LDAP auth does not require password
        assert user.role is db.Role.admin

    @pytest.mark.parametrize("user_role", list(db.Role))
    def test_authorize_user_has_user(
        self,
        test_system_user_storage: SystemUserStorage,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_db_groups: list[str],
        test_username: str,
        user_role: db.Role,
    ) -> None:
        mocked_ldap_authenticator.get_user_groups.return_value = test_db_groups
        with create_test_session() as session:
            test_system_user_storage.create_user(session=session, login=test_username, role=user_role)
        with count_queries(1):
            user = test_ldap_auth_manager.authorize_user(
                username=test_username, password=SecretStr(None)  # type: ignore
            )
        assert user is not None
        assert user.login == test_username
        assert user.password is None  # LDAP auth does not require password
        assert user.role is user_role


@pytest.mark.usefixtures("database")
class TestDefaultAuthManager:
    """Integration tests for :class:`DefaultAdminAuthorizationManager`."""

    def test_authorize_user_no_user(
        self,
        test_default_auth_manager: DefaultAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        with count_queries(1):
            assert test_default_auth_manager.authorize_user(username=test_username, password=test_password) is None

    @pytest.mark.parametrize("user_role", list(db.Role))
    def test_authorize_user_has_user(
        self,
        test_system_user_storage: SystemUserStorage,
        test_default_auth_manager: DefaultAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
        user_role: db.Role,
    ) -> None:
        with create_test_session() as session:
            test_system_user_storage.create_user(
                session=session, login=test_username, password=test_password, role=user_role
            )
        with count_queries(1):
            user = test_default_auth_manager.authorize_user(username=test_username, password=test_password)
        assert user is not None
        assert user.login == test_username
        assert user.password is not None
        assert user.password.get_secret_value() == test_password.get_secret_value()
        assert user.role is user_role


@pytest.mark.usefixtures("database")
class TestSimpleAuthManager:
    """Integration tests for :class:`SimpleAdminAuthorizationManager`."""

    def test_authorize_user_no_user(
        self,
        test_simple_auth_manager: SimpleAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        with count_queries(2):
            user = test_simple_auth_manager.authorize_user(username=test_username, password=test_password)
        assert user is not None
        assert user.login == test_username
        assert user.password is not None
        assert user.password.get_secret_value() == test_password.get_secret_value()
        assert user.role is db.Role.user

    @pytest.mark.parametrize("user_role", list(db.Role))
    def test_authorize_user_has_user(
        self,
        test_system_user_storage: SystemUserStorage,
        test_simple_auth_manager: SimpleAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
        user_role: db.Role,
    ) -> None:
        with create_test_session() as session:
            test_system_user_storage.create_user(
                session=session, login=test_username, password=test_password, role=user_role
            )
        with count_queries(1):
            user = test_simple_auth_manager.authorize_user(username=test_username, password=test_password)
        assert user is not None
        assert user.login == test_username
        assert user.password is not None
        assert user.password.get_secret_value() == test_password.get_secret_value()
        assert user.role is user_role

    def test_authorize_user_incorrect_password(
        self,
        test_system_user_storage: SystemUserStorage,
        test_simple_auth_manager: SimpleAdminAuthorizationManager,
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        with create_test_session() as session:
            test_system_user_storage.create_user(session=session, login=test_username, password=test_password)
        incorrect_password_field = MagicMock()
        incorrect_password_field.data = "incorrect_password"
        with count_queries(1):
            user = test_simple_auth_manager.authorize_user(username=test_username, password=incorrect_password_field)
        assert user is None
