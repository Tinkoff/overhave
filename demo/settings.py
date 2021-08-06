import enum
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
from overhave.publication.gitlab import OverhaveGitlabPublisherSettings, TokenizerClientSettings
from overhave.publication.objects import PublicationManagerType
from overhave.publication.settings import PublicationSettings
from overhave.transport import OverhaveGitlabClientSettings


class OverhaveDemoAppLanguage(str, enum.Enum):
    """ Enum for choice of Overhave demo application language. """

    RU = "RU"
    EN = "EN"


class OverhaveDemoSettingsGenerator:
    """ Settings for application demo mode configuration. """

    def __init__(self, language: OverhaveDemoAppLanguage, threadpool: bool):
        self._root_dir: Path = Path(__file__).parent
        self._language = language
        self._threadpool = threadpool

    @cached_property
    def default_context_settings(self) -> Dict[str, BaseSettings]:
        if self._language is OverhaveDemoAppLanguage.RU:
            language_settings = OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES)
        else:
            language_settings = OverhaveLanguageSettings()
        return dict(
            language_settings=language_settings, file_settings=OverhaveFileSettings(root_dir=self._root_dir.as_posix()),
        )

    @cached_property
    def admin_context_settings(self) -> Dict[str, BaseSettings]:
        settings: Dict[str, BaseSettings] = dict(
            admin_settings=OverhaveAdminSettings(consumer_based=not self._threadpool)
        )
        settings.update(self.default_context_settings)
        return settings

    @cached_property
    def publication_context_settings(self) -> Dict[str, BaseSettings]:
        settings = deepcopy(self.default_context_settings)
        if PublicationSettings().publication_manager_type is PublicationManagerType.GITLAB:
            publication_manager_settings = dict(
                publisher_settings=OverhaveGitlabPublisherSettings(repository_id="4687"),
                client_settings=OverhaveGitlabClientSettings(  # noqa: S106
                    url="https://overhave.readthedocs.io/not-a-handler",
                ),
                tokenizer_client_settings=TokenizerClientSettings(),
            )
            settings.update(publication_manager_settings)
            return settings
        publication_manager_settings = dict(
            publisher_settings=OverhaveStashPublisherSettings(repository_name="bdd-features", project_key="OVH"),
            client_settings=OverhaveStashClientSettings(  # noqa: S106
                url="https://overhave.readthedocs.io/not-a-handler", auth_token="secret_token"
            ),
        )
        settings.update(publication_manager_settings)
        return settings
