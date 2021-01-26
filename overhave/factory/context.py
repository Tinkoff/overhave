from typing import Optional

from overhave.entities import (
    OverhaveEmulationSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveScenarioCompilerSettings,
    ProcessorSettings,
)
from overhave.entities.authorization.settings import (
    OverhaveAdminSettings,
    OverhaveAuthorizationSettings,
    OverhaveLdapClientSettings,
)
from overhave.stash.settings import OverhaveStashClientSettings, OverhaveStashProjectSettings
from overhave.testing import OverhaveProjectSettings, OverhaveTestSettings


class OverhaveContext:
    """ Application Context, based on BaseSettings.

    This context defines how Overhave application will work.
    """

    def __init__(
        self,
        admin_settings: Optional[OverhaveAdminSettings] = None,
        auth_settings: Optional[OverhaveAuthorizationSettings] = None,
        compilation_settings: Optional[OverhaveScenarioCompilerSettings] = None,
        emulation_settings: Optional[OverhaveEmulationSettings] = None,
        file_settings: Optional[OverhaveFileSettings] = None,
        language_settings: Optional[OverhaveLanguageSettings] = None,
        ldap_client_settings: Optional[OverhaveLdapClientSettings] = None,
        processor_settings: Optional[ProcessorSettings] = None,
        project_settings: Optional[OverhaveProjectSettings] = None,
        stash_client_settings: Optional[OverhaveStashClientSettings] = None,
        stash_project_settings: Optional[OverhaveStashProjectSettings] = None,
        test_settings: Optional[OverhaveTestSettings] = None,
    ) -> None:
        self.admin_settings = admin_settings or OverhaveAdminSettings()
        self.auth_settings = auth_settings or OverhaveAuthorizationSettings()
        self.compilation_settings = compilation_settings or OverhaveScenarioCompilerSettings()
        self.emulation_settings = emulation_settings or OverhaveEmulationSettings()
        self.file_settings = file_settings or OverhaveFileSettings()
        self.language_settings = language_settings or OverhaveLanguageSettings()
        self.ldap_client_settings = ldap_client_settings or OverhaveLdapClientSettings()
        self.processor_settings = processor_settings or ProcessorSettings()
        self.project_settings = project_settings or OverhaveProjectSettings()
        self.stash_client_settings = stash_client_settings or OverhaveStashClientSettings()
        self.stash_project_settings = stash_project_settings or OverhaveStashProjectSettings()
        self.test_settings = test_settings or OverhaveTestSettings()
