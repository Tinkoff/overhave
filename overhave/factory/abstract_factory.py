import abc

from overhave.entities import FileManager, IFeatureExtractor, IProcessor
from overhave.entities.authorization.manager import IAdminAuthorizationManager
from overhave.entities.emulator import Emulator
from overhave.factory.context import OverhaveContext
from overhave.pytest import ConfigInjector, PytestRunner
from overhave.redis import RedisProducer
from overhave.storage import IEmulationStorage, IFeatureTypeStorage


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
