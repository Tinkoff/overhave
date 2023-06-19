import abc

from overhave import db
from overhave.transport import PublicationTask


class IVersionPublisher(abc.ABC):
    """Abstract class for feature version's pull requests management."""

    @abc.abstractmethod
    def publish_version(self, draft_id: int) -> db.DraftStatus:
        pass

    @abc.abstractmethod
    def process_publish_task(self, task: PublicationTask) -> None:
        pass
