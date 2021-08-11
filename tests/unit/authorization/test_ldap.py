from pydantic import SecretStr

from overhave.authorization import LDAPAuthenticator
from tests.unit.authorization.conftest import TEST_LDAP_GROUPS


class TestLdapAuthenticator:
    """ Unit tests for :class:`LDAPAuthenticator`. """

    def test_get_user_groups(self, test_ldap_authenticator: LDAPAuthenticator) -> None:
        assert test_ldap_authenticator.get_user_groups("kek", SecretStr("lol")) == TEST_LDAP_GROUPS
