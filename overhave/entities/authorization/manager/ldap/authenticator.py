import logging
import re
from typing import List, Optional

import ldap
from ldap.ldapobject import LDAPObject

from overhave.entities.authorization.settings import OverhaveLdapClientSettings

logger = logging.getLogger(__name__)


class LDAPAuthenticator:
    """ Class-client for LDAP authentication. """

    def __init__(self, settings: OverhaveLdapClientSettings) -> None:
        self._settings = settings
        self._ldap_connection: Optional[LDAPObject] = None

    def _connect(self, login: str, password: str) -> None:
        ldap_connection = ldap.initialize(self._settings.ldap_url)
        ldap_connection.set_option(ldap.OPT_REFERRALS, 0)
        ldap_connection.set_option(ldap.OPT_NETWORK_TIMEOUT, self._settings.ldap_timeout.seconds)
        ldap_connection.simple_bind_s(f'{self._settings.ldap_domain}{login}', password)

        self._ldap_connection = ldap_connection

    def _ask_ad_usergroups(self, login: str) -> List[str]:
        result = self._ldap_connection.search_st(  # type: ignore
            base=self._settings.ldap_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=f"(sAMAccountName={login})",
            attrlist=['memberOf'],
            timeout=self._settings.ldap_timeout.seconds,
        )
        member_of = result[0][1]['memberOf']
        member_of = [m.decode('utf8') for m in member_of]

        p = re.compile('CN=(.*?),', re.IGNORECASE)
        return [
            p.match(x).group(1)  # type: ignore
            for x in list(filter(lambda x: 'OU=Security Groups' in x or 'OU=Mail Groups' in x, member_of))
        ]

    def get_user_groups(self, login: str, password: str) -> Optional[List[str]]:
        try:
            self._connect(login, password)
        except ldap.INVALID_CREDENTIALS:
            logger.info('Failed LDAP authorization for user: %s', login)
            return None

        return self._ask_ad_usergroups(login)
