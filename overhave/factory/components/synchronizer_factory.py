import abc
from functools import cached_property

from overhave.factory.base_factory import BaseOverhaveFactory, IOverhaveFactory
from overhave.factory.context import OverhaveSynchronizerContext
from overhave.scenario import FeatureValidator
from overhave.synchronization import IOverhaveSynchronizer, OverhaveSynchronizer, SynchronizerStorageManager


class ISynchronizerFactory(IOverhaveFactory[OverhaveSynchronizerContext]):
    """Factory interface for Overhave feature synchronizer application."""

    @property
    @abc.abstractmethod
    def synchronizer(self) -> IOverhaveSynchronizer:
        pass

    @property
    @abc.abstractmethod
    def feature_validator(self) -> FeatureValidator:
        pass


class SynchronizerFactory(BaseOverhaveFactory[OverhaveSynchronizerContext], ISynchronizerFactory):
    """Factory for Overhave feature synchronization application."""

    context_cls = OverhaveSynchronizerContext

    @cached_property
    def _synchronizer(self) -> OverhaveSynchronizer:
        return OverhaveSynchronizer(
            file_settings=self.context.file_settings,
            scenario_parser=self._scenario_parser,
            feature_extractor=self._feature_extractor,
            git_initializer=self._git_initializer,
            storage_manager=SynchronizerStorageManager(
                feature_storage=self._feature_storage,
                feature_type_storage=self._feature_type_storage,
                scenario_storage=self._scenario_storage,
                tag_storage=self._feature_tag_storage,
                draft_storage=self._draft_storage,
                system_user_storage=self._system_user_storage,
            ),
        )

    @property
    def synchronizer(self) -> IOverhaveSynchronizer:
        return self._synchronizer

    @cached_property
    def _feature_validator(self) -> FeatureValidator:
        return FeatureValidator(
            file_settings=self.context.file_settings,
            scenario_parser=self._scenario_parser,
            git_initializer=self._git_initializer,
        )

    @property
    def feature_validator(self) -> FeatureValidator:
        return self._feature_validator
