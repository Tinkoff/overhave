from overhave.base_settings import BaseOverhavePrefix


class OverhaveLdapManagerSettings(BaseOverhavePrefix):
    """Settings for Overhave LDAP auth_managers manager."""

    ldap_admin_group: str
