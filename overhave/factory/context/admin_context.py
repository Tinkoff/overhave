from typing import Optional

from overhave.entities import (
    OverhaveEmulationSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveRedisSettings,
    OverhaveReportManagerSettings,
)
from overhave.entities.authorization import AuthorizationStrategy
from overhave.entities.authorization.settings import (
    OverhaveAdminSettings,
    OverhaveAuthorizationSettings,
    OverhaveLdapClientSettings,
)
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.test_execution import OverhaveProjectSettings, OverhaveTestSettings
from overhave.transport import OverhaveS3ManagerSettings


class OverhaveAdminContext(BaseFactoryContext):
    """ Overhave admin context, based on application BaseSettings.

    This context defines how Overhave admin will work.
    """

    def __init__(
        self,
        admin_settings: Optional[OverhaveAdminSettings] = None,
        auth_settings: Optional[OverhaveAuthorizationSettings] = None,
        emulation_settings: Optional[OverhaveEmulationSettings] = None,
        file_settings: Optional[OverhaveFileSettings] = None,
        language_settings: Optional[OverhaveLanguageSettings] = None,
        ldap_client_settings: Optional[OverhaveLdapClientSettings] = None,
        redis_settings: Optional[OverhaveRedisSettings] = None,
        report_manager_settings: Optional[OverhaveReportManagerSettings] = None,
        project_settings: Optional[OverhaveProjectSettings] = None,
        s3_manager_settings: Optional[OverhaveS3ManagerSettings] = None,
        test_settings: Optional[OverhaveTestSettings] = None,
    ) -> None:
        super().__init__(
            emulation_settings=emulation_settings or OverhaveEmulationSettings(),
            file_settings=file_settings or OverhaveFileSettings(),
            language_settings=language_settings or OverhaveLanguageSettings(),
            project_settings=project_settings or OverhaveProjectSettings(),
            report_manager_settings=report_manager_settings or OverhaveReportManagerSettings(),
            s3_manager_settings=s3_manager_settings or OverhaveS3ManagerSettings(),
            test_settings=test_settings or OverhaveTestSettings(),
        )
        self.admin_settings = admin_settings or OverhaveAdminSettings()
        self.auth_settings = auth_settings or OverhaveAuthorizationSettings()
        self.redis_settings = redis_settings or OverhaveRedisSettings()
        if self.auth_settings.auth_strategy is AuthorizationStrategy.LDAP:
            self.ldap_client_settings = ldap_client_settings or OverhaveLdapClientSettings()
