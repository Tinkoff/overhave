from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import Dict

from pydantic import BaseSettings

from overhave import (
    OverhaveAdminSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveStashClientSettings,
    OverhaveStashPublisherSettings,
)
from overhave.extra import RUSSIAN_PREFIXES
from overhave.factory import get_admin_factory
from overhave.publication.gitlab import OverhaveGitlabPublisherSettings
from overhave.test_execution.settings import OverhaveProjectSettings, PublicationManagerType
from overhave.transport import OverhaveGitlabClientSettings


class OverhaveDemoSettingsGenerator:
    """ Settings for application demo mode configuration. """

    root_dir: Path = Path(__file__).parent

    @cached_property
    def default_context_settings(self) -> Dict[str, BaseSettings]:
        return dict(
            language_settings=OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES),
            file_settings=OverhaveFileSettings(root_dir=self.root_dir.as_posix()),
        )

    def get_admin_context_settings(self, threadpool: bool) -> Dict[str, BaseSettings]:
        settings: Dict[str, BaseSettings] = dict(admin_settings=OverhaveAdminSettings(consumer_based=not threadpool))
        settings.update(self.default_context_settings)
        return settings

    @cached_property
    def publication_settings(self) -> Dict[str, BaseSettings]:
        settings = deepcopy(self.default_context_settings)
        publication_manager_type = OverhaveProjectSettings().publication_manager_type
        if publication_manager_type is PublicationManagerType.GITLAB:
            settings["client_settings"] = OverhaveGitlabClientSettings(
                url="https://overhave.readthedocs.io/not-a-handler", auth_token="secret_token"
            )
            settings["publisher_settings"] = OverhaveGitlabPublisherSettings(repository_id="2034")
            return settings
        settings["client_settings"] = OverhaveStashClientSettings(
            url="https://overhave.readthedocs.io/not-a-handler", auth_token="secret_token"
        )
        settings["publisher_settings"] = OverhaveStashPublisherSettings(
            repository_name="bdd-features", project_key="OVH"
        )
        return settings
