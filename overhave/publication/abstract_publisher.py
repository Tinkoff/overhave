import abc

from overhave.transport import PublicationTask


class IVersionPublisher(abc.ABC):
    """ Abstract class for feature version's pull requests management. """

    @abc.abstractmethod
    def publish_version(self, task: PublicationTask) -> None:
        pass
