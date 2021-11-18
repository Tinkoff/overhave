from typing import List, Sequence
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from overhave import db
from overhave.authorization import (
    DefaultAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    SimpleAdminAuthorizationManager,
)
from overhave.storage import SystemUserStorage


def _create_user_groups(db_groups: Sequence[str]) -> None:
    with db.create_session() as session:
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

        user = test_ldap_auth_manager.authorize_user(username=test_username, password=test_password)
        assert user is not None
        assert user.login == test_username
        assert user.password is None  # LDAP auth does not require password
        assert user.role is db.Role.user

    def test_authorize_user_no_user_admin_group(
        self,
        test_admin_group: str,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_db_groups: List[str],
        test_username: str,
        test_password: SecretStr,
    ) -> None:
        db_groups = [test_admin_group] + test_db_groups
        mocked_ldap_authenticator.get_user_groups.return_value = db_groups
        _create_user_groups(db_groups)

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
        test_db_groups: List[str],
        test_username: str,
        user_role: db.Role,
    ) -> None:
        mocked_ldap_authenticator.get_user_groups.return_value = test_db_groups
        test_system_user_storage.create_user(login=test_username, role=user_role)
        user = test_ldap_auth_manager.authorize_user(username=test_username, password=SecretStr(None))  # type: ignore
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
        test_system_user_storage.create_user(login=test_username, password=test_password, role=user_role)
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
        test_system_user_storage.create_user(login=test_username, password=test_password, role=user_role)
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
        test_system_user_storage.create_user(login=test_username, password=test_password)
        incorrect_password_field = MagicMock()
        incorrect_password_field.data = "incorrect_password"
        assert (
            test_simple_auth_manager.authorize_user(username=test_username, password=incorrect_password_field) is None
        )
