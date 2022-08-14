import abc
from functools import cached_property
from typing import Generic, Optional, Type, cast

from overhave.entities import (
    ArchiveManager,
    FeatureExtractor,
    GitRepositoryInitializer,
    IFeatureExtractor,
    ReportManager,
)
from overhave.factory.context import TApplicationContext
from overhave.scenario import FileManager, ScenarioCompiler, ScenarioParser
from overhave.storage import (
    DraftStorage,
    EmulationStorage,
    FeatureStorage,
    FeatureTagStorage,
    FeatureTypeStorage,
    IDraftStorage,
    IEmulationStorage,
    IFeatureTypeStorage,
    IScenarioStorage,
    ISystemUserStorage,
    ITestRunStorage,
    ScenarioStorage,
    SystemUserStorage,
    TestRunStorage,
)
from overhave.test_execution import PytestRunner, StepCollector
from overhave.transport import S3Manager


class IOverhaveFactory(Generic[TApplicationContext], abc.ABC):
    """Factory interface for application entities resolution and usage."""

    @abc.abstractmethod
    def set_context(self, context: TApplicationContext) -> None:
        pass

    @property
    @abc.abstractmethod
    def context(self) -> TApplicationContext:
        pass

    @property
    @abc.abstractmethod
    def draft_storage(self) -> IDraftStorage:
        pass

    @property
    @abc.abstractmethod
    def emulation_storage(self) -> IEmulationStorage:
        pass

    @property
    @abc.abstractmethod
    def feature_extractor(self) -> IFeatureExtractor:
        pass

    @property
    @abc.abstractmethod
    def scenario_parser(self) -> ScenarioParser:
        pass

    @property
    @abc.abstractmethod
    def scenario_storage(self) -> IScenarioStorage:
        pass

    @property
    @abc.abstractmethod
    def step_collector(self) -> StepCollector:
        pass

    @property
    @abc.abstractmethod
    def test_run_storage(self) -> ITestRunStorage:
        pass

    @property
    @abc.abstractmethod
    def test_runner(self) -> PytestRunner:
        pass

    @property
    @abc.abstractmethod
    def system_user_storage(self) -> ISystemUserStorage:
        pass


class BaseOverhaveFactory(IOverhaveFactory[TApplicationContext]):
    """Base factory for application entities resolution and usage."""

    context_cls: Type[TApplicationContext]

    def __init__(self) -> None:
        self._context: Optional[TApplicationContext] = None

    def set_context(self, context: TApplicationContext) -> None:
        self._context = context

    @property
    def context(self) -> TApplicationContext:
        if self._context is None:
            self.set_context(self.context_cls())
        return cast(TApplicationContext, self._context)

    @cached_property
    def _archive_manager(self) -> ArchiveManager:
        return ArchiveManager(file_settings=self.context.file_settings)

    @cached_property
    def _draft_storage(self) -> DraftStorage:
        return DraftStorage()

    @property
    def draft_storage(self) -> IDraftStorage:
        return self._draft_storage

    @cached_property
    def _emulation_storage(self) -> EmulationStorage:
        return EmulationStorage(settings=self.context.emulation_settings)

    @property
    def emulation_storage(self) -> IEmulationStorage:
        return self._emulation_storage

    @cached_property
    def _feature_extractor(self) -> FeatureExtractor:
        return FeatureExtractor(file_settings=self.context.file_settings)

    @property
    def feature_extractor(self) -> IFeatureExtractor:
        return self._feature_extractor

    @cached_property
    def _feature_tag_storage(self) -> FeatureTagStorage:
        return FeatureTagStorage()

    @cached_property
    def _feature_storage(self) -> FeatureStorage:
        return FeatureStorage()

    @cached_property
    def _feature_type_storage(self) -> IFeatureTypeStorage:
        return FeatureTypeStorage()

    @cached_property
    def _file_manager(self) -> FileManager:
        for path in (
            self.context.file_settings.tmp_features_dir,
            self.context.file_settings.tmp_fixtures_dir,
            self.context.file_settings.tmp_reports_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
        return FileManager(
            project_settings=self.context.project_settings,
            file_settings=self.context.file_settings,
            feature_extractor=self._feature_extractor,
            scenario_compiler=self._scenario_compiler,
        )

    @cached_property
    def _report_manager(self) -> ReportManager:
        return ReportManager(
            settings=self.context.report_manager_settings,
            file_settings=self.context.file_settings,
            test_run_storage=self._test_run_storage,
            archive_manager=self._archive_manager,
            s3_manager=self._s3_manager,
        )

    @property
    def report_manager(self) -> ReportManager:
        return self._report_manager

    @cached_property
    def _s3_manager(self) -> S3Manager:
        return S3Manager(self.context.s3_manager_settings)

    @cached_property
    def _scenario_compiler(self) -> ScenarioCompiler:
        return ScenarioCompiler(
            compilation_settings=self.context.compilation_settings,
            language_settings=self.context.language_settings,
            tasks_keyword=self.context.project_settings.tasks_keyword,
        )

    @cached_property
    def _scenario_parser(self) -> ScenarioParser:
        return ScenarioParser(
            parser_settings=self.context.parser_settings,
            compilation_settings=self.context.compilation_settings,
            language_settings=self.context.language_settings,
            feature_extractor=self._feature_extractor,
            tasks_keyword=self.context.project_settings.tasks_keyword,
        )

    @property
    def scenario_parser(self) -> ScenarioParser:
        return self._scenario_parser

    @cached_property
    def _scenario_storage(self) -> IScenarioStorage:
        return ScenarioStorage()

    @property
    def scenario_storage(self) -> IScenarioStorage:
        return self._scenario_storage

    @cached_property
    def _step_collector(self) -> StepCollector:
        return StepCollector(step_prefixes=self.context.language_settings.step_prefixes)

    @property
    def step_collector(self) -> StepCollector:
        return self._step_collector

    @cached_property
    def _test_run_storage(self) -> TestRunStorage:
        return TestRunStorage()

    @property
    def test_run_storage(self) -> ITestRunStorage:
        return self._test_run_storage

    @cached_property
    def _test_runner(self) -> PytestRunner:
        return PytestRunner(settings=self.context.test_settings)

    @property
    def test_runner(self) -> PytestRunner:
        return self._test_runner

    @cached_property
    def _system_user_storage(self) -> ISystemUserStorage:
        return SystemUserStorage()

    @property
    def system_user_storage(self) -> ISystemUserStorage:
        return self._system_user_storage

    @cached_property
    def _git_initializer(self) -> GitRepositoryInitializer:
        return GitRepositoryInitializer(file_settings=self.context.file_settings)
