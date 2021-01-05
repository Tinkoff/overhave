from typing import Any, Dict, Iterator, Optional
from unittest import mock
from unittest.mock import MagicMock

import pytest

from overhave.entities.authorization.manager import LDAPAuthenticator
from overhave.entities.authorization.settings import LdapClientSettings


@pytest.fixture(scope="session")
def envs_for_mock() -> Dict[str, Optional[str]]:
    return {
        'OVERHAVE_LDAP_URL': 'ldap://mydomain.ru',
        "OVERHAVE_LDAP_DOMAIN": "domain\\",
        "OVERHAVE_LDAP_DN": "dc=example,dc=ru",
    }


@pytest.fixture(scope="module")
def mock_urls(envs_for_mock: Dict[str, Optional[str]]) -> Iterator[None]:
    import os

    old_values = {key: os.environ.get(key) for key in envs_for_mock}
    try:
        for key in envs_for_mock:
            os.environ[key] = envs_for_mock.get('envs_for_mock') or "http://dummy"
        yield
    finally:
        for key, value in old_values.items():
            os.environ[key] = value or ''


@pytest.fixture()
def test_ldap_client_settings(mock_urls: None) -> LdapClientSettings:
    return LdapClientSettings()


TEST_LDAP_GROUPS = ['group1', 'group2']


def mocked_ldap_connection(cls: Any, *args: Any, **kwargs: Any) -> None:
    cls._ldap_connection = MagicMock()
    cls._ldap_connection.search_st.return_value = [
        (
            'CN=Very cool member,OU=dep1,DC=mydomain,DC=ru',
            {
                'memberOf': [
                    bytes(f'CN={TEST_LDAP_GROUPS[0]},OU=dep1,OU=Security Groups,DC=mydomain,DC=ru', encoding='utf-8'),
                    bytes(f'CN={TEST_LDAP_GROUPS[1]},OU=dep2,OU=Security Groups,DC=mydomain,DC=ru', encoding='utf-8'),
                ]
            },
        )
    ]


@pytest.fixture()
def test_ldap_authenticator(test_ldap_client_settings: LdapClientSettings) -> Iterator[LDAPAuthenticator]:
    with mock.patch.object(LDAPAuthenticator, '_connect', new=mocked_ldap_connection):
        yield LDAPAuthenticator(settings=test_ldap_client_settings)
