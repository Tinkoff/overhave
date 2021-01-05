import abc

from overhave.stash.models import StashPrCreationResponse


class IStashProjectManager(abc.ABC):
    @abc.abstractmethod
    def create_pull_request(self, test_run_id: int) -> StashPrCreationResponse:
        pass
