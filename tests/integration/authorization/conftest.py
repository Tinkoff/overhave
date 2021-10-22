from typing import List, cast

import pytest
from faker import Faker
from pydantic import SecretStr
from pytest_mock import MockFixture

from overhave import OverhaveAuthorizationSettings
from overhave.authorization import (
    DefaultAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    LDAPAuthenticator,
    SimpleAdminAuthorizationManager,
)
from overhave.storage import SystemUserGroupStorage, SystemUserStorage


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
    test_system_user_storage: SystemUserStorage,
    test_system_user_group_storage: SystemUserGroupStorage,
    mocked_ldap_authenticator: LDAPAuthenticator,
    test_auth_settings: OverhaveAuthorizationSettings,
) -> LDAPAdminAuthorizationManager:
    return LDAPAdminAuthorizationManager(
        settings=test_auth_settings,
        system_user_storage=test_system_user_storage,
        system_user_group_storage=test_system_user_group_storage,
        ldap_authenticator=mocked_ldap_authenticator,
    )


@pytest.fixture()
def test_default_auth_manager(
    test_system_user_storage: SystemUserStorage, test_auth_settings: OverhaveAuthorizationSettings
) -> DefaultAdminAuthorizationManager:
    return DefaultAdminAuthorizationManager(settings=test_auth_settings, system_user_storage=test_system_user_storage)


@pytest.fixture()
def test_simple_auth_manager(
    test_system_user_storage: SystemUserStorage, test_auth_settings: OverhaveAuthorizationSettings
) -> SimpleAdminAuthorizationManager:
    return SimpleAdminAuthorizationManager(settings=test_auth_settings, system_user_storage=test_system_user_storage)


@pytest.fixture()
def test_username(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_password(faker: Faker) -> SecretStr:
    return SecretStr(faker.word())
