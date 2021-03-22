from functools import cached_property

from overhave.factory.base_factory import BaseOverhaveFactory
from overhave.factory.components.abstract_consumer import ITaskConsumerFactory
from overhave.factory.context import OverhavePublicationContext
from overhave.publication import IVersionPublisher, StashVersionPublisher
from overhave.transport import PublicationTask, StashHttpClient


class PublicationFactory(BaseOverhaveFactory[OverhavePublicationContext], ITaskConsumerFactory[PublicationTask]):
    """ Factory for Overhave publication application. """

    context_cls = OverhavePublicationContext

    @cached_property
    def _stash_client(self) -> StashHttpClient:
        return StashHttpClient(settings=self.context.stash_client_settings)

    @cached_property
    def _stash_publisher(self) -> IVersionPublisher:
        return StashVersionPublisher(
            file_settings=self.context.file_settings,
            project_settings=self.context.project_settings,
            feature_storage=self._feature_storage,
            scenario_storage=self._scenario_storage,
            test_run_storage=self._test_run_storage,
            draft_storage=self._draft_storage,
            file_manager=self._file_manager,
            stash_publisher_settings=self.context.stash_publisher_settings,
            client=self._stash_client,
        )

    def process_task(self, task: PublicationTask) -> None:
        return self._stash_publisher.publish_version(task)
