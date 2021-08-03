import abc
from functools import cached_property

from overhave.factory.base_factory import BaseOverhaveFactory, IOverhaveFactory
from overhave.factory.components.abstract_consumer import ITaskConsumerFactory
from overhave.factory.context import OverhavePublicationContext
from overhave.publication import IVersionPublisher, StashVersionPublisher
from overhave.publication.gitlab import GitlabVersionPublisher, TokenizerClient
from overhave.publication.objects import PublicationManagerType
from overhave.transport import GitlabHttpClient, PublicationTask, StashHttpClient


class BasePublicationFactoryException(Exception):
    """ Base exception for :class:`PublicationFactory`. """


class AuthTokenNotSpecifiedError(BasePublicationFactoryException):
    """ Exception for situation AuthToken env was not set. """


class UrlGitlabTokenizerNotScepifiedIfEnabled(BasePublicationFactoryException):
    """ Exception for situation tokenizer is enabled and url env was not set. """


class IPublicationFactory(IOverhaveFactory[OverhavePublicationContext], ITaskConsumerFactory[PublicationTask], abc.ABC):
    """ Abstract factory for Overhave publication application. """

    @property
    @abc.abstractmethod
    def publisher(self) -> IVersionPublisher:
        pass


class PublicationFactory(BaseOverhaveFactory[OverhavePublicationContext], IPublicationFactory):
    """ Factory for Overhave publication application. """

    context_cls = OverhavePublicationContext

    @cached_property
    def _stash_client(self) -> StashHttpClient:
        return StashHttpClient(self.context.client_settings)  # type: ignore

    @cached_property
    def _gitlab_client(self) -> GitlabHttpClient:
        return GitlabHttpClient(self.context.client_settings)  # type: ignore

    @cached_property
    def _stash_publisher(self) -> StashVersionPublisher:
        return StashVersionPublisher(
            file_settings=self.context.file_settings,
            project_settings=self.context.project_settings,
            feature_storage=self._feature_storage,
            scenario_storage=self._scenario_storage,
            test_run_storage=self._test_run_storage,
            draft_storage=self._draft_storage,
            file_manager=self._file_manager,
            stash_publisher_settings=self.context.publisher_settings,  # type: ignore
            client=self._stash_client,
        )

    @cached_property
    def _tokenizer_client(self) -> TokenizerClient:
        return TokenizerClient(self.context.tokenizer_client_settings)

    @cached_property
    def _gitlab_publisher(self) -> GitlabVersionPublisher:
        if not self._tokenizer_client._settings.enabled and self._gitlab_client._settings.auth_token is None:
            raise AuthTokenNotSpecifiedError("Please set correct auth_token!")
        if self._tokenizer_client._settings.enabled and self._tokenizer_client._settings.url is None:
            raise UrlGitlabTokenizerNotScepifiedIfEnabled("Please set correct url for gitlab_tokenizer!")
        return GitlabVersionPublisher(
            file_settings=self.context.file_settings,
            project_settings=self.context.project_settings,
            feature_storage=self._feature_storage,
            scenario_storage=self._scenario_storage,
            test_run_storage=self._test_run_storage,
            draft_storage=self._draft_storage,
            file_manager=self._file_manager,
            gitlab_publisher_settings=self.context.publisher_settings,  # type: ignore
            gitlab_client=self._gitlab_client,
            tokenizer_client=self._tokenizer_client,
        )

    @property
    def publisher(self) -> IVersionPublisher:
        if self.context.publication_settings.publication_manager_type is PublicationManagerType.GITLAB:
            return self._gitlab_publisher
        return self._stash_publisher

    def process_task(self, task: PublicationTask) -> None:
        return self.publisher.process_publish_task(task)
