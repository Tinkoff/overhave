import abc

from overhave.entities import Emulator, IAdminAuthorizationManager, IFeatureExtractor
from overhave.factory.context import OverhaveContext
from overhave.processing import IProcessor
from overhave.redis import RedisProducer
from overhave.scenario import FileManager
from overhave.storage import IEmulationStorage, IFeatureTypeStorage
from overhave.testing import ConfigInjector, PytestRunner


class IOverhaveFactory(abc.ABC):
    """ Factory interface for application entities resolution and usage. """

    @abc.abstractmethod
    def set_context(self, context: OverhaveContext) -> None:
        pass

    @property
    @abc.abstractmethod
    def context(self) -> OverhaveContext:
        pass

    @property
    @abc.abstractmethod
    def test_runner(self) -> PytestRunner:
        pass

    @property
    @abc.abstractmethod
    def feature_extractor(self) -> IFeatureExtractor:
        pass

    @property
    @abc.abstractmethod
    def file_manager(self) -> FileManager:
        pass

    @property
    @abc.abstractmethod
    def injector(self) -> ConfigInjector:
        pass

    @property
    @abc.abstractmethod
    def processor(self) -> IProcessor:
        pass

    @property
    @abc.abstractmethod
    def auth_manager(self) -> IAdminAuthorizationManager:
        pass

    @property
    @abc.abstractmethod
    def feature_type_storage(self) -> IFeatureTypeStorage:
        pass

    @property
    @abc.abstractmethod
    def redis_producer(self) -> RedisProducer:
        pass

    @property
    @abc.abstractmethod
    def emulation_storage(self) -> IEmulationStorage:
        pass

    @property
    @abc.abstractmethod
    def emulator(self) -> Emulator:
        pass
