import enum
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import Dict

from pydantic import BaseSettings
from yarl import URL

from overhave import (
    OverhaveAdminLinkSettings,
    OverhaveAdminSettings,
    OverhaveFileSettings,
    OverhaveGitlabClientSettings,
    OverhaveGitlabPublisherSettings,
    OverhaveLanguageSettings,
    OverhaveProjectSettings,
    OverhavePublicationManagerType,
    OverhavePublicationSettings,
    OverhaveStashClientSettings,
    OverhaveStashPublisherSettings,
)
from overhave.extra import RUSSIAN_PREFIXES
from overhave.publication.gitlab import TokenizerClientSettings


class OverhaveDemoAppLanguage(str, enum.Enum):
    """Enum for choice of Overhave demo application language."""

    RU = "ru"
    EN = "en"


class OverhaveDemoSettingsGenerator:
    """Settings for application demo mode configuration."""

    def __init__(
        self,
        admin_host: str,
        admin_port: int,
        language: OverhaveDemoAppLanguage,
        threadpool: bool,
        default_feature_user: str = "user",
    ):
        self._root_dir: Path = Path(__file__).parent

        self._admin_host = admin_host
        self._admin_port = admin_port
        self._language = language
        self._threadpool = threadpool
        self._default_feature_user = default_feature_user  # default user login from demo feature files

    @property
    def admin_host(self) -> str:
        return self._admin_host

    @property
    def admin_port(self) -> int:
        return self._admin_port

    @property
    def default_feature_user(self) -> str:
        return self._default_feature_user

    @cached_property
    def default_context_settings(self) -> Dict[str, BaseSettings]:
        if self._language is OverhaveDemoAppLanguage.RU:
            language_settings = OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES)
        else:
            language_settings = OverhaveLanguageSettings()
        return dict(
            language_settings=language_settings,
            file_settings=OverhaveFileSettings(root_dir=self._root_dir.as_posix()),
            project_settings=OverhaveProjectSettings(
                task_tracker_url="https://tasktracker.myorg.com/browse",
                tasks_keyword="Tasks",
                git_project_url="https://ci.myorg.com/project/bdd-features",
            ),
        )

    @cached_property
    def test_execution_settings(self) -> Dict[str, BaseSettings]:
        admin_url = URL(self._admin_host)
        if not admin_url.scheme:
            admin_url = URL(f"http://{self._admin_host}:{self._admin_port}")
        settings: Dict[str, BaseSettings] = dict(
            admin_link_settings=OverhaveAdminLinkSettings(admin_url=admin_url.human_repr())
        )
        settings.update(self.default_context_settings)
        return settings

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
        if OverhavePublicationSettings().publication_manager_type is OverhavePublicationManagerType.GITLAB:
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
