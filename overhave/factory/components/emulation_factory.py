import abc
from functools import cached_property

from overhave.entities import Emulator
from overhave.factory import IOverhaveFactory
from overhave.factory.base_factory import BaseOverhaveFactory
from overhave.factory.context import OverhaveEmulationContext


class IEmulationFactory(IOverhaveFactory[OverhaveEmulationContext]):
    """ Factory interface for Overhave emulation application. """

    @property
    @abc.abstractmethod
    def emulator(self) -> Emulator:
        pass


class EmulationFactory(BaseOverhaveFactory[OverhaveEmulationContext], IEmulationFactory):
    """ Factory for Overhave emulation application. """

    @cached_property
    def _emulator(self) -> Emulator:
        return Emulator(settings=self.context.emulation_settings, storage=self._emulation_storage)

    @property
    def emulator(self) -> Emulator:
        return self._emulator
