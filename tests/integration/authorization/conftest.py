from typing import cast

import pytest
from faker import Faker
from pydantic import SecretStr
from pytest_mock import MockFixture

from overhave.entities import (
    DefaultAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    OverhaveLdapManagerSettings,
    SimpleAdminAuthorizationManager,
)
from overhave.storage import SystemUserGroupStorage, SystemUserStorage
from overhave.transport import LDAPAuthenticator
from tests.db_utils import create_test_session


@pytest.fixture()
def mocked_ldap_authenticator(mocker: MockFixture) -> LDAPAuthenticator:
    return cast(LDAPAuthenticator, mocker.create_autospec(LDAPAuthenticator))


@pytest.fixture()
def test_admin_group(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_db_groups(test_admin_group: str, faker: Faker) -> list[str]:
    groups: list[str] = ["my", "unique", "groupnames"]
    while test_admin_group in groups:
        groups.remove(test_admin_group)
        groups.append(faker.word())
    return groups


@pytest.fixture()
def test_ldap_manager_settings(test_admin_group: str) -> OverhaveLdapManagerSettings:
    return OverhaveLdapManagerSettings(ldap_admin_group=test_admin_group)


@pytest.fixture()
def test_ldap_auth_manager(
    test_system_user_storage: SystemUserStorage,
    test_system_user_group_storage: SystemUserGroupStorage,
    mocked_ldap_authenticator: LDAPAuthenticator,
    test_ldap_manager_settings: OverhaveLdapManagerSettings,
) -> LDAPAdminAuthorizationManager:
    return LDAPAdminAuthorizationManager(
        settings=test_ldap_manager_settings,
        system_user_storage=test_system_user_storage,
        system_user_group_storage=test_system_user_group_storage,
        ldap_authenticator=mocked_ldap_authenticator,
    )


@pytest.fixture()
def test_default_auth_manager(test_system_user_storage: SystemUserStorage) -> DefaultAdminAuthorizationManager:
    with create_test_session():
        return DefaultAdminAuthorizationManager(system_user_storage=test_system_user_storage)


@pytest.fixture()
def test_simple_auth_manager(test_system_user_storage: SystemUserStorage) -> SimpleAdminAuthorizationManager:
    with create_test_session():
        return SimpleAdminAuthorizationManager(system_user_storage=test_system_user_storage)


@pytest.fixture()
def test_username(faker: Faker) -> str:
    return faker.word()


@pytest.fixture()
def test_password(faker: Faker) -> SecretStr:
    return SecretStr(faker.word())
