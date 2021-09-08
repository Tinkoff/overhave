import abc


class IOverhaveSynchronizer(abc.ABC):
    """ Abstract class for synchronization between git and database. """

    @abc.abstractmethod
    def synchronize(self) -> None:
        pass
