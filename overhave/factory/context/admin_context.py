from overhave.base_settings import AuthorizationStrategy, OverhaveAuthorizationSettings
from overhave.entities import (
    OverhaveAdminSettings,
    OverhaveEmulationSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveLdapManagerSettings,
    OverhaveReportManagerSettings,
)
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.scenario import OverhaveProjectSettings, OverhaveScenarioCompilerSettings
from overhave.test_execution import OverhaveStepCollectorSettings, OverhaveTestSettings
from overhave.transport import OverhaveLdapClientSettings, OverhaveS3ManagerSettings


class OverhaveAdminContext(BaseFactoryContext):
    """Overhave admin context, based on application BaseSettings.

    This context defines how Overhave admin will work.
    """

    def __init__(
        self,
        admin_settings: OverhaveAdminSettings | None = None,
        auth_settings: OverhaveAuthorizationSettings | None = None,
        emulation_settings: OverhaveEmulationSettings | None = None,
        file_settings: OverhaveFileSettings | None = None,
        language_settings: OverhaveLanguageSettings | None = None,
        ldap_manager_settings: OverhaveLdapManagerSettings | None = None,
        ldap_client_settings: OverhaveLdapClientSettings | None = None,
        project_settings: OverhaveProjectSettings | None = None,
        compilation_settings: OverhaveScenarioCompilerSettings | None = None,
        report_manager_settings: OverhaveReportManagerSettings | None = None,
        s3_manager_settings: OverhaveS3ManagerSettings | None = None,
        test_settings: OverhaveTestSettings | None = None,
        step_collector_settings: OverhaveStepCollectorSettings | None = None,
    ) -> None:
        super().__init__(
            emulation_settings=emulation_settings or OverhaveEmulationSettings(),
            file_settings=file_settings or OverhaveFileSettings(),
            language_settings=language_settings or OverhaveLanguageSettings(),
            project_settings=project_settings or OverhaveProjectSettings(),
            compilation_settings=compilation_settings or OverhaveScenarioCompilerSettings(),
            report_manager_settings=report_manager_settings or OverhaveReportManagerSettings(),
            s3_manager_settings=s3_manager_settings or OverhaveS3ManagerSettings(),
            test_settings=test_settings or OverhaveTestSettings(),
            step_collector_settings=step_collector_settings or OverhaveStepCollectorSettings(),
        )
        self.admin_settings = admin_settings or OverhaveAdminSettings()
        self.auth_settings = auth_settings or OverhaveAuthorizationSettings()
        if self.auth_settings.auth_strategy is AuthorizationStrategy.LDAP:
            self.ldap_manager_settings = ldap_manager_settings or OverhaveLdapManagerSettings()
            self.ldap_client_settings = ldap_client_settings or OverhaveLdapClientSettings()
