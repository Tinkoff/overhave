from typing import List, cast

import pytest
from faker import Faker
from pytest_mock import MockFixture
from wtforms import PasswordField, StringField

from overhave import OverhaveAuthorizationSettings
from overhave.entities.authorization.manager import (
    DefaultAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    LDAPAuthenticator,
    SimpleAdminAuthorizationManager,
)


@pytest.fixture()
def mocked_ldap_authenticator(mocker: MockFixture) -> LDAPAuthenticator:
    return cast(LDAPAuthenticator, mocker.create_autospec(LDAPAuthenticator))


@pytest.fixture()
def test_admin_group(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_db_groups(test_admin_group: str, faker: Faker) -> List[str]:
    groups: List[str] = ["my", "unique", "groupnames"]
    while test_admin_group in groups:
        groups.remove(test_admin_group)
        groups.append(faker.word())
    return groups


@pytest.fixture()
def test_auth_settings(test_admin_group: str) -> OverhaveAuthorizationSettings:
    return OverhaveAuthorizationSettings(admin_group=test_admin_group)


@pytest.fixture()
def test_ldap_auth_manager(
    mocked_ldap_authenticator: LDAPAuthenticator, test_auth_settings: OverhaveAuthorizationSettings
) -> LDAPAdminAuthorizationManager:
    return LDAPAdminAuthorizationManager(settings=test_auth_settings, ldap_authenticator=mocked_ldap_authenticator)


@pytest.fixture()
def test_default_auth_manager(test_auth_settings: OverhaveAuthorizationSettings) -> DefaultAdminAuthorizationManager:
    return DefaultAdminAuthorizationManager(settings=test_auth_settings)


@pytest.fixture()
def test_simple_auth_manager(test_auth_settings: OverhaveAuthorizationSettings) -> SimpleAdminAuthorizationManager:
    return SimpleAdminAuthorizationManager(settings=test_auth_settings)


@pytest.fixture()
def test_username(mocker: MockFixture, faker: Faker) -> StringField:
    field = mocker.create_autospec(StringField)
    field.data = faker.word()
    return field


@pytest.fixture()
def test_password(mocker: MockFixture, faker: Faker) -> PasswordField:
    field = mocker.create_autospec(PasswordField)
    field.data = faker.word()
    return field
