from pydantic.datetime_parse import timedelta

from overhave.base_settings import BaseOverhavePrefix


class OverhaveLdapManagerSettings(BaseOverhavePrefix):
    """Settings for Overhave LDAP authorization manager."""

    ldap_admin_group: str


class OverhaveLdapClientSettings(BaseOverhavePrefix):
    """Settings for Overhave LDAP client."""

    ldap_url: str  # for example: "ldap://mydomain.ru"
    ldap_domain: str  # for example: "domain\\"
    ldap_dn: str  # for example: "dc=example,dc=com"
    ldap_timeout: timedelta = timedelta(seconds=10)
