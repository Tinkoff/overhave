from typing import Optional, Union

from overhave.entities import OverhaveFileSettings, OverhaveLanguageSettings, OverhaveScenarioCompilerSettings
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.publication import OverhaveStashPublisherSettings
from overhave.publication.gitlab import OverhaveGitlabPublisherSettings
from overhave.publication.gitlab.tokenizer.settings import TokenizerClientSettings
from overhave.publication.settings import PublicationSettings
from overhave.test_execution import OverhaveProjectSettings
from overhave.transport import OverhaveGitlabClientSettings, OverhaveStashClientSettings


class OverhavePublicationContext(BaseFactoryContext):
    """ Overhave publication context, based on application BaseSettings.

    This context defines how Overhave publication will work.
    """

    def __init__(
        self,
        compilation_settings: Optional[OverhaveScenarioCompilerSettings] = None,
        file_settings: Optional[OverhaveFileSettings] = None,
        language_settings: Optional[OverhaveLanguageSettings] = None,
        project_settings: Optional[OverhaveProjectSettings] = None,
        client_settings: Optional[Union[OverhaveStashClientSettings, OverhaveGitlabClientSettings]] = None,
        publisher_settings: Optional[Union[OverhaveStashPublisherSettings, OverhaveGitlabPublisherSettings]] = None,
        publication_settings: Optional[PublicationSettings] = None,
        tokenizer_client_settings: Optional[TokenizerClientSettings] = None,
    ) -> None:
        super().__init__(
            compilation_settings=compilation_settings or OverhaveScenarioCompilerSettings(),
            file_settings=file_settings or OverhaveFileSettings(),
            language_settings=language_settings or OverhaveLanguageSettings(),
            project_settings=project_settings or OverhaveProjectSettings(),
        )
        self.client_settings = client_settings or OverhaveGitlabClientSettings()
        self.publisher_settings = publisher_settings or OverhaveGitlabPublisherSettings()
        self.publication_settings = publication_settings or PublicationSettings()
        self.tokenizer_client_settings = tokenizer_client_settings or TokenizerClientSettings()
        if not self.tokenizer_client_settings.enabled and self.client_settings.auth_token is None:
            raise ValueError("Please set correct auth_token!")
