from overhave.entities import OverhaveFileSettings, OverhaveLanguageSettings
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.publication.gitlab import OverhaveGitlabPublisherSettings, TokenizerClientSettings
from overhave.publication.settings import BaseGitPublisherSettings, PublicationSettings
from overhave.scenario import OverhaveProjectSettings, OverhaveScenarioCompilerSettings
from overhave.transport import OverhaveGitlabClientSettings
from overhave.transport.http.base_client.settings import HttpSettingsType


class OverhavePublicationContext(BaseFactoryContext):
    """Overhave publication context, based on application BaseSettings.

    This context defines how Overhave publication will work.
    """

    def __init__(
        self,
        compilation_settings: OverhaveScenarioCompilerSettings | None = None,
        file_settings: OverhaveFileSettings | None = None,
        language_settings: OverhaveLanguageSettings | None = None,
        project_settings: OverhaveProjectSettings | None = None,
        client_settings: HttpSettingsType | None = None,
        publisher_settings: BaseGitPublisherSettings | None = None,
        publication_settings: PublicationSettings | None = None,
        tokenizer_client_settings: TokenizerClientSettings | None = None,
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
