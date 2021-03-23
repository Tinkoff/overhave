import abc
from functools import cached_property

from overhave.entities import Emulator
from overhave.factory.base_factory import BaseOverhaveFactory, IOverhaveFactory
from overhave.factory.components.abstract_consumer import ITaskConsumerFactory
from overhave.factory.context import OverhaveEmulationContext
from overhave.transport import EmulationTask


class IEmulationFactory(IOverhaveFactory[OverhaveEmulationContext], ITaskConsumerFactory[EmulationTask], abc.ABC):
    """ Abstract factory for Overhave emulation application. """


class EmulationFactory(BaseOverhaveFactory[OverhaveEmulationContext], IEmulationFactory):
    """ Factory for Overhave emulation application. """

    context_cls = OverhaveEmulationContext

    @cached_property
    def _emulator(self) -> Emulator:
        return Emulator(settings=self.context.emulation_settings, storage=self._emulation_storage)

    def process_task(self, task: EmulationTask) -> None:
        return self._emulator.start_emulation(task)
