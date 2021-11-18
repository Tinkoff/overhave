import abc

from overhave.transport import PublicationTask


class IVersionPublisher(abc.ABC):
    """Abstract class for feature version's pull requests management."""

    @abc.abstractmethod
    def publish_version(self, draft_id: int) -> None:
        pass

    @abc.abstractmethod
    def process_publish_task(self, task: PublicationTask) -> None:
        pass
