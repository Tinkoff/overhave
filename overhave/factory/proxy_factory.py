from overhave.entities import Emulator, IAdminAuthorizationManager, IFeatureExtractor
from overhave.factory.abstract_factory import IOverhaveFactory
from overhave.factory.context import OverhaveContext
from overhave.processing import IProcessor
from overhave.redis import RedisProducer
from overhave.scenario import FileManager
from overhave.storage import IEmulationStorage, IFeatureTypeStorage
from overhave.testing import ConfigInjector, PytestRunner


class ProxyFactory(IOverhaveFactory):
    """ Factory for application entities resolution and usage, based on proxy-object pattern.

    Class inherits :class:`IOverhaveFactory` and realise logic for dynamic entities resolution before and
    during application or tests start-up. In fact, it is a proxy-object for :class:`OverhaveBaseFactory`.
    """

    def __init__(self) -> None:
        from overhave.factory.base_factory import OverhaveBaseFactory

        self._factory = OverhaveBaseFactory()
        self._pytest_patched = False
        self._collection_prepared = False

    def set_context(self, context: OverhaveContext) -> None:
        self._factory.set_context(context)

    @property
    def context(self) -> OverhaveContext:
        return self._factory.context

    @property
    def test_runner(self) -> PytestRunner:
        return self._factory.test_runner

    @property
    def file_manager(self) -> FileManager:
        return self._factory.file_manager

    @property
    def injector(self) -> ConfigInjector:
        return self._factory.injector

    @property
    def feature_extractor(self) -> IFeatureExtractor:
        return self._factory.feature_extractor

    def patch_pytest(self) -> None:
        if not self._pytest_patched:
            self._factory.injector.patch_pytestbdd_prefixes(
                custom_step_prefixes=self._factory.context.language_settings.step_prefixes
            )
            self._pytest_patched = True

    @property
    def pytest_patched(self) -> bool:
        return self._pytest_patched

    def supply_injector_for_collection(self) -> None:
        if not self._collection_prepared:
            self._factory.injector.supplement_on_fly(
                project_settings=self._factory.context.project_settings,
                file_settings=self._factory.context.file_settings,
                step_collector=self._factory.step_collector,
                test_runner=self._factory.test_runner,
                feature_types=self._factory.feature_extractor.feature_types,
            )
            self._collection_prepared = True

    @property
    def processor(self) -> IProcessor:
        return self._factory.processor

    @property
    def auth_manager(self) -> IAdminAuthorizationManager:
        return self._factory.auth_manager

    @property
    def emulator(self) -> Emulator:
        return self._factory.emulator

    @property
    def feature_type_storage(self) -> IFeatureTypeStorage:
        return self._factory.feature_type_storage

    @property
    def redis_producer(self) -> RedisProducer:
        return self._factory.redis_producer

    @property
    def emulation_storage(self) -> IEmulationStorage:
        return self._factory.emulation_storage
