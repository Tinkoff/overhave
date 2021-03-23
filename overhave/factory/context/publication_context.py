from typing import Optional

from overhave.entities import OverhaveFileSettings, OverhaveLanguageSettings, OverhaveScenarioCompilerSettings
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.publication import OverhaveStashPublisherSettings
from overhave.test_execution import OverhaveProjectSettings
from overhave.transport import OverhaveStashClientSettings


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
        stash_client_settings: Optional[OverhaveStashClientSettings] = None,
        stash_publisher_settings: Optional[OverhaveStashPublisherSettings] = None,
    ) -> None:
        super().__init__(
            compilation_settings=compilation_settings or OverhaveScenarioCompilerSettings(),
            file_settings=file_settings or OverhaveFileSettings(),
            language_settings=language_settings or OverhaveLanguageSettings(),
            project_settings=project_settings or OverhaveProjectSettings(),
        )
        self.stash_client_settings = stash_client_settings or OverhaveStashClientSettings()
        self.stash_publisher_settings = stash_publisher_settings or OverhaveStashPublisherSettings()
