import abc


class IOverhaveSynchronizer(abc.ABC):
    """Abstract class for synchronization between git and database."""

    @abc.abstractmethod
    def synchronize(self, create_db_features: bool = False, pull_repository: bool = False) -> None:
        pass
