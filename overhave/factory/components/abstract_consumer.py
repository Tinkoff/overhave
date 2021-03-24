import abc
from typing import Generic

from overhave.transport import TRedisTask


class ITaskConsumerFactory(Generic[TRedisTask], abc.ABC):
    """ Abstract class for factory, which consumes `TRedisTask` tasks. """

    @abc.abstractmethod
    def process_task(self, task: TRedisTask) -> None:
        pass
