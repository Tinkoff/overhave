from typing import Optional

from overhave.entities import (
    OverhaveDescriptionManagerSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveReportManagerSettings,
    OverhaveScenarioCompilerSettings,
    OverhaveStepContextSettings,
)
from overhave.test_execution import OverhaveProjectSettings, OverhaveTestSettings
from overhave.transport import S3ManagerSettings


class OverhaveTestExecutionContext:
    """ Overhave test run context, based on application BaseSettings.

    This context defines how Overhave test run will work.
    """

    def __init__(
        self,
        compilation_settings: Optional[OverhaveScenarioCompilerSettings] = None,
        description_manager_settings: Optional[OverhaveDescriptionManagerSettings] = None,
        file_settings: Optional[OverhaveFileSettings] = None,
        language_settings: Optional[OverhaveLanguageSettings] = None,
        project_settings: Optional[OverhaveProjectSettings] = None,
        report_manager_settings: Optional[OverhaveReportManagerSettings] = None,
        s3_manager_settings: Optional[S3ManagerSettings] = None,
        step_context_settings: Optional[OverhaveStepContextSettings] = None,
        test_settings: Optional[OverhaveTestSettings] = None,
    ) -> None:
        self.compilation_settings = compilation_settings or OverhaveScenarioCompilerSettings()
        self.description_manager_settings = description_manager_settings or OverhaveDescriptionManagerSettings()
        self.file_settings = file_settings or OverhaveFileSettings()
        self.language_settings = language_settings or OverhaveLanguageSettings()
        self.project_settings = project_settings or OverhaveProjectSettings()
        self.report_manager_settings = report_manager_settings or OverhaveReportManagerSettings()
        self.s3_manager_settings = s3_manager_settings or S3ManagerSettings()
        self.step_context_settings = step_context_settings or OverhaveStepContextSettings()
        self.test_settings = test_settings or OverhaveTestSettings()
