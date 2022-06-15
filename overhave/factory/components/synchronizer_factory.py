import abc
from functools import cached_property

from overhave.factory.base_factory import BaseOverhaveFactory, IOverhaveFactory
from overhave.factory.context import OverhaveSynchronizerContext
from overhave.synchronization import IOverhaveSynchronizer, OverhaveSynchronizer


class ISynchronizerFactory(IOverhaveFactory[OverhaveSynchronizerContext]):
    """Factory interface for Overhave feature synchronizer application."""

    @property
    @abc.abstractmethod
    def synchronizer(self) -> IOverhaveSynchronizer:
        pass


class SynchronizerFactory(BaseOverhaveFactory[OverhaveSynchronizerContext], ISynchronizerFactory):
    """Factory for Overhave feature synchronization application."""

    context_cls = OverhaveSynchronizerContext

    @cached_property
    def _synchronizer(self) -> OverhaveSynchronizer:
        return OverhaveSynchronizer(
            file_settings=self.context.file_settings,
            feature_storage=self._feature_storage,
            feature_type_storage=self._feature_type_storage,
            scenario_storage=self._scenario_storage,
            draft_storage=self._draft_storage,
            tag_storage=self._feature_tag_storage,
            scenario_parser=self._scenario_parser,
            feature_extractor=self._feature_extractor,
            system_user_storage=self._system_user_storage,
            git_initializer=self._git_initializer,
        )

    @property
    def synchronizer(self) -> IOverhaveSynchronizer:
        return self._synchronizer
