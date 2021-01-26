from pathlib import Path
from typing import Optional

from pydantic.datetime_parse import timedelta

from overhave.base_settings import BaseOverhavePrefix
from overhave.entities.authorization.strategies import AuthorizationStrategy


class OverhaveAdminSettings(BaseOverhavePrefix):
    """ Settings for Overhave Flask Admin customization. """

    # Path to custom index template. By default, contains Overhave project info.
    index_template_path: Optional[Path]


class OverhaveAuthorizationSettings(BaseOverhavePrefix):
    """ Settings for Overhave authorization in admin interface.

    Supports 3 strategies: SIMPLE, DEFAULT and LDAP.
    LDAP authorization uses group politics with administration group `admin_group`.
    SIMPLE and DEFAULT strategies use admin user that would be dynamically created at startup.
    """

    auth_strategy: AuthorizationStrategy = AuthorizationStrategy.DEFAULT
    admin_group: Optional[str] = None


class OverhaveLdapClientSettings(BaseOverhavePrefix):
    """ Settings for Overhave LDAP client for AuthorizationStrategy.LDAP strategy. """

    ldap_url: str  # for example: "ldap://mydomain.ru"
    ldap_domain: str  # for example: "domain\\"
    ldap_dn: str  # for example: "dc=example,dc=com"
    ldap_timeout: timedelta = timedelta(seconds=10)
