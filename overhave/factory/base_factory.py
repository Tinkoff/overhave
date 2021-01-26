from functools import cached_property
from os import makedirs
from typing import Any, Dict, Optional

from overhave.entities import FeatureExtractor, IFeatureExtractor, OverhaveRedisSettings
from overhave.entities.authorization.manager import IAdminAuthorizationManager, LDAPAuthenticator
from overhave.entities.authorization.mapping import AUTH_STRATEGY_TO_MANAGER_MAPPING, AuthorizationStrategy
from overhave.entities.emulator import EmulationTask, Emulator
from overhave.factory.abstract_factory import IOverhaveFactory
from overhave.factory.context import OverhaveContext
from overhave.processing import IProcessor
from overhave.redis import RedisProducer, RedisStream
from overhave.scenario import FileManager, ScenarioCompiler, ScenarioParser
from overhave.stash import IStashProjectManager, StashClient
from overhave.storage import EmulationStorage, FeatureTypeStorage, IEmulationStorage, IFeatureTypeStorage
from overhave.testing import ConfigInjector, PytestRunner, StepCollector


class OverhaveBaseFactory(IOverhaveFactory):
    """ Base factory for application entities resolution and usage. """

    def __init__(self) -> None:
        self._context: Optional[OverhaveContext] = None

    def set_context(self, context: OverhaveContext) -> None:
        self._context = context

    @property
    def has_context(self) -> bool:
        return self._context is not None

    @property
    def context(self) -> OverhaveContext:
        if self._context is None:
            self._context = OverhaveContext()
        return self._context

    @cached_property
    def _test_runner(self) -> PytestRunner:
        return PytestRunner(test_settings=self.context.test_settings)

    @property
    def test_runner(self) -> PytestRunner:
        return self._test_runner

    @property
    def step_collector(self) -> StepCollector:
        return StepCollector(step_prefixes=self.context.language_settings.step_prefixes)

    @cached_property
    def _injector(self) -> ConfigInjector:
        return ConfigInjector()

    @property
    def injector(self) -> ConfigInjector:
        return self._injector

    @cached_property
    def _feature_extractor(self) -> IFeatureExtractor:
        return FeatureExtractor(file_settings=self.context.file_settings)

    @property
    def feature_extractor(self) -> IFeatureExtractor:
        return self._feature_extractor

    @cached_property
    def _file_manager(self) -> FileManager:
        for path in (
            self.context.file_settings.tmp_features_dir,
            self.context.file_settings.tmp_fixtures_dir,
            self.context.file_settings.tmp_reports_dir,
        ):
            makedirs(path.as_posix(), exist_ok=True)
        return FileManager(
            project_settings=self.context.project_settings,
            file_settings=self.context.file_settings,
            language_settings=self.context.language_settings,
            feature_extractor=self._feature_extractor,
            scenario_compiler=ScenarioCompiler(
                compilation_settings=self.context.compilation_settings,
                language_settings=self.context.language_settings,
                task_links_keyword=self.context.project_settings.links_keyword,
            ),
            scenario_parser=ScenarioParser(
                compilation_settings=self.context.compilation_settings,
                language_settings=self.context.language_settings,
                feature_extractor=self._feature_extractor,
                task_links_keyword=self.context.project_settings.links_keyword,
            ),
        )

    @property
    def file_manager(self) -> FileManager:
        return self._file_manager

    @cached_property
    def _stash_client(self) -> StashClient:
        return StashClient(settings=self.context.stash_client_settings)

    @cached_property
    def _stash_manager(self) -> IStashProjectManager:
        from overhave.stash.manager.manager import StashProjectManager

        return StashProjectManager(
            stash_project_settings=self.context.stash_project_settings,
            file_settings=self.context.file_settings,
            client=self._stash_client,
            file_manager=self._file_manager,
            task_links_keyword=self.context.project_settings.links_keyword,
        )

    @cached_property
    def _processor(self) -> IProcessor:
        from overhave.processing.processor import Processor

        return Processor(
            settings=self.context.processor_settings,
            file_settings=self.context.file_settings,
            injector=self._injector,
            file_manager=self._file_manager,
            test_runner=self._test_runner,
            stash_manager=self._stash_manager,
        )

    @property
    def processor(self) -> IProcessor:
        return self._processor

    @cached_property
    def _auth_manager(self) -> IAdminAuthorizationManager:
        settings = self.context.auth_settings
        kwargs: Dict[str, Any] = dict(settings=settings)
        if settings.auth_strategy is AuthorizationStrategy.LDAP:
            kwargs["ldap_authenticator"] = LDAPAuthenticator(settings=self.context.ldap_client_settings)
        return AUTH_STRATEGY_TO_MANAGER_MAPPING[settings.auth_strategy](**kwargs)  # type: ignore

    @property
    def auth_manager(self) -> IAdminAuthorizationManager:
        return self._auth_manager

    @cached_property
    def _emulator(self) -> Emulator:
        return Emulator(storage=self._emulation_storage, settings=self.context.emulation_settings)

    @property
    def emulator(self) -> Emulator:
        return self._emulator

    @cached_property
    def _feature_type_storage(self) -> IFeatureTypeStorage:
        return FeatureTypeStorage()

    @property
    def feature_type_storage(self) -> IFeatureTypeStorage:
        return self._feature_type_storage

    @cached_property
    def _redis_producer(self) -> RedisProducer:
        return RedisProducer(settings=OverhaveRedisSettings(), mapping={EmulationTask: RedisStream.EMULATION})

    @property
    def redis_producer(self) -> RedisProducer:
        return self._redis_producer

    @cached_property
    def _emulation_storage(self) -> IEmulationStorage:
        return EmulationStorage(settings=self.context.emulation_settings)

    @property
    def emulation_storage(self) -> IEmulationStorage:
        return self._emulation_storage
