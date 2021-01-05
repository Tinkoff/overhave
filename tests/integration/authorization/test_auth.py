from typing import List, Sequence
from unittest.mock import MagicMock

import pytest
from wtforms import PasswordField, StringField

from overhave import db
from overhave.entities.authorization.manager import (
    DefaultAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    SimpleAdminAuthorizationManager,
)


def _create_user_groups(db_groups: Sequence[str]) -> None:
    with db.create_session() as session:
        for group in db_groups:
            session.add(db.GroupRole(group=group))


@pytest.mark.usefixtures("database")
class TestLdapAuthManager:
    def test_authorize_user_no_groups(
        self,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
    ):
        mocked_ldap_authenticator.get_user_groups.return_value = []
        assert test_ldap_auth_manager.authorize_user(username_field=test_username, password_field=test_password) is None

    def test_authorize_user_no_user_no_groups(
        self,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
    ):
        mocked_ldap_authenticator.get_user_groups.return_value = ["not_supplied_group"]
        assert test_ldap_auth_manager.authorize_user(username_field=test_username, password_field=test_password) is None

    def test_authorize_user_no_user_has_group(
        self,
        test_db_groups: Sequence[str],
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
    ):
        mocked_ldap_authenticator.get_user_groups.return_value = test_db_groups
        _create_user_groups(test_db_groups)

        user = test_ldap_auth_manager.authorize_user(username_field=test_username, password_field=test_password)
        assert user is not None
        assert user.login == test_username.data
        assert user.password is None  # LDAP auth does not require password
        assert user.role is db.Role.user

    def test_authorize_user_no_user_admin_group(
        self,
        test_admin_group: str,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_db_groups: List[str],
        test_username: StringField,
        test_password: PasswordField,
    ):
        db_groups = [test_admin_group] + test_db_groups
        mocked_ldap_authenticator.get_user_groups.return_value = db_groups
        _create_user_groups(db_groups)

        user = test_ldap_auth_manager.authorize_user(username_field=test_username, password_field=test_password)
        assert user is not None
        assert user.login == test_username.data
        assert user.password is None  # LDAP auth does not require password
        assert user.role is db.Role.admin

    @pytest.mark.parametrize("user_role", list(db.Role))
    def test_authorize_user_has_user(
        self,
        mocked_ldap_authenticator: MagicMock,
        test_ldap_auth_manager: LDAPAdminAuthorizationManager,
        test_db_groups: List[str],
        test_username: StringField,
        test_password: PasswordField,
        user_role: db.Role,
    ):
        mocked_ldap_authenticator.get_user_groups.return_value = test_db_groups
        with db.create_session() as session:
            session.add(db.UserRole(login=test_username.data, password=None, role=user_role))

        user = test_ldap_auth_manager.authorize_user(username_field=test_username, password_field=test_password)
        assert user is not None
        assert user.login == test_username.data
        assert user.password is None  # LDAP auth does not require password
        assert user.role is user_role


@pytest.mark.usefixtures("database")
class TestDefaultAuthManager:
    def test_authorize_user_no_user(
        self,
        test_default_auth_manager: DefaultAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
    ):
        assert (
            test_default_auth_manager.authorize_user(username_field=test_username, password_field=test_password) is None
        )

    @pytest.mark.parametrize("user_role", list(db.Role))
    def test_authorize_user_has_user(
        self,
        test_default_auth_manager: DefaultAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
        user_role: db.Role,
    ):
        with db.create_session() as session:
            session.add(db.UserRole(login=test_username.data, password=test_password.data, role=user_role))

        user = test_default_auth_manager.authorize_user(username_field=test_username, password_field=test_password)
        assert user is not None
        assert user.login == test_username.data
        assert user.password == test_password.data
        assert user.role is user_role


@pytest.mark.usefixtures("database")
class TestSimpleAuthManager:
    def test_authorize_user_no_user(
        self,
        test_simple_auth_manager: SimpleAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
    ):
        user = test_simple_auth_manager.authorize_user(username_field=test_username, password_field=test_password)
        assert user is not None
        assert user.login == test_username.data
        assert user.password == test_password.data
        assert user.role is db.Role.user

    @pytest.mark.parametrize("user_role", list(db.Role))
    def test_authorize_user_has_user(
        self,
        test_simple_auth_manager: SimpleAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
        user_role: db.Role,
    ):
        with db.create_session() as session:
            session.add(db.UserRole(login=test_username.data, password=test_password.data, role=user_role))

        user = test_simple_auth_manager.authorize_user(username_field=test_username, password_field=test_password)
        assert user is not None
        assert user.login == test_username.data
        assert user.password == test_password.data
        assert user.role is user_role

    def test_authorize_user_incorrect_password(
        self,
        test_simple_auth_manager: SimpleAdminAuthorizationManager,
        test_username: StringField,
        test_password: PasswordField,
    ):
        with db.create_session() as session:
            session.add(db.UserRole(login=test_username.data, password=test_password.data, role=db.Role.user))

        incorrect_password_field = MagicMock()
        incorrect_password_field.data = "incorrect_password"

        assert (
            test_simple_auth_manager.authorize_user(
                username_field=test_username, password_field=incorrect_password_field
            )
            is None
        )
