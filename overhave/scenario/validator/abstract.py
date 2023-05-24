import abc


class IFeatureValidator(abc.ABC):
    """Interface for features validation."""

    @abc.abstractmethod
    def validate(self, raise_if_nullable_id: bool = False, pull_repository: bool = False) -> None:
        pass
