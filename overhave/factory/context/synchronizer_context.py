from typing import Optional

from overhave.entities import OverhaveFileSettings, OverhaveLanguageSettings
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.scenario import OverhaveProjectSettings, OverhaveScenarioCompilerSettings, OverhaveScenarioParserSettings


class OverhaveSynchronizerContext(BaseFactoryContext):
    """Overhave feature synchronizer context, based on application BaseSettings.

    This context defines how Overhave admin will work.
    """

    def __init__(
        self,
        file_settings: Optional[OverhaveFileSettings] = None,
        compilation_settings: Optional[OverhaveScenarioCompilerSettings] = None,
        parser_settings: Optional[OverhaveScenarioParserSettings] = None,
        language_settings: Optional[OverhaveLanguageSettings] = None,
        project_settings: Optional[OverhaveProjectSettings] = None,
    ) -> None:
        super().__init__(
            file_settings=file_settings or OverhaveFileSettings(),
            compilation_settings=compilation_settings or OverhaveScenarioCompilerSettings(),
            parser_settings=parser_settings or OverhaveScenarioParserSettings(),
            language_settings=language_settings or OverhaveLanguageSettings(),
            project_settings=project_settings or OverhaveProjectSettings(),
        )
