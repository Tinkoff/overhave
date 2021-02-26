import abc

from overhave.transport.http.stash_client import StashPrCreationResponse


class IStashProjectManager(abc.ABC):
    """ Abstract class for feature pull requests management. """

    @abc.abstractmethod
    def create_pull_request(self, test_run_id: int) -> StashPrCreationResponse:
        pass
