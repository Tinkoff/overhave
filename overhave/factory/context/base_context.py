from typing import cast

from pydantic_settings import BaseSettings

from overhave.entities import (
    OverhaveEmulationSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveReportManagerSettings,
)
from overhave.scenario import OverhaveProjectSettings, OverhaveScenarioCompilerSettings, OverhaveScenarioParserSettings
from overhave.test_execution import OverhaveStepCollectorSettings, OverhaveTestSettings
from overhave.transport import OverhaveS3ManagerSettings


class BaseFactoryContextException(Exception):
    """Base exception for :class:`BaseFactoryContext`."""


class NotDefinedSettingsError(BaseFactoryContextException):
    """Exception for situation with not defined specific settings."""


class BaseFactoryContext:
    """Base class for factory context."""

    def __init__(
        self,
        compilation_settings: OverhaveScenarioCompilerSettings | None = None,
        parser_settings: OverhaveScenarioParserSettings | None = None,
        emulation_settings: OverhaveEmulationSettings | None = None,
        file_settings: OverhaveFileSettings | None = None,
        language_settings: OverhaveLanguageSettings | None = None,
        project_settings: OverhaveProjectSettings | None = None,
        report_manager_settings: OverhaveReportManagerSettings | None = None,
        s3_manager_settings: OverhaveS3ManagerSettings | None = None,
        test_settings: OverhaveTestSettings | None = None,
        step_collector_settings: OverhaveStepCollectorSettings | None = None,
    ):
        self._compilation_settings = compilation_settings
        self._parser_settings = parser_settings
        self._emulation_settings = emulation_settings
        self._file_settings = file_settings
        self._language_settings = language_settings
        self._project_settings = project_settings
        self._report_manager_settings = report_manager_settings
        self._s3_manager_settings = s3_manager_settings
        self._test_settings = test_settings
        self._step_collector_settings = step_collector_settings

    @staticmethod
    def _ensured_settings(settings: BaseSettings | None) -> BaseSettings:
        if settings is None:
            raise NotDefinedSettingsError(type(settings).__name__)
        return settings

    @property
    def compilation_settings(self) -> OverhaveScenarioCompilerSettings:
        return cast(OverhaveScenarioCompilerSettings, self._ensured_settings(self._compilation_settings))

    @property
    def parser_settings(self) -> OverhaveScenarioParserSettings:
        return cast(OverhaveScenarioParserSettings, self._ensured_settings(self._parser_settings))

    @property
    def emulation_settings(self) -> OverhaveEmulationSettings:
        return cast(OverhaveEmulationSettings, self._ensured_settings(self._emulation_settings))

    @property
    def file_settings(self) -> OverhaveFileSettings:
        return cast(OverhaveFileSettings, self._ensured_settings(self._file_settings))

    @property
    def language_settings(self) -> OverhaveLanguageSettings:
        return cast(OverhaveLanguageSettings, self._ensured_settings(self._language_settings))

    @property
    def project_settings(self) -> OverhaveProjectSettings:
        return cast(OverhaveProjectSettings, self._ensured_settings(self._project_settings))

    @property
    def report_manager_settings(self) -> OverhaveReportManagerSettings:
        return cast(OverhaveReportManagerSettings, self._ensured_settings(self._report_manager_settings))

    @property
    def s3_manager_settings(self) -> OverhaveS3ManagerSettings:
        return cast(OverhaveS3ManagerSettings, self._ensured_settings(self._s3_manager_settings))

    @property
    def test_settings(self) -> OverhaveTestSettings:
        return cast(OverhaveTestSettings, self._ensured_settings(self._test_settings))

    @property
    def step_collector_settings(self) -> OverhaveStepCollectorSettings:
        return cast(OverhaveStepCollectorSettings, self._ensured_settings(self._step_collector_settings))
