import logging

from requests import HTTPError

from overhave.entities import OverhaveFileSettings, PublisherContext
from overhave.publication.git_publisher import BaseGitVersionPublisherError, GitVersionPublisher
from overhave.publication.gitlab.settings import OverhaveGitlabPublisherSettings
from overhave.scenario import FileManager
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
from overhave.test_execution import OverhaveProjectSettings
from overhave.transport.http.gitlab_client import (
    GitlabErrorResponse,
    GitlabHttpClient,
    GitlabHttpClientConflictError,
    GitlabMrRequest,
)
from overhave.transport.http.gitlab_client.models import GitlabBranch, GitlabMrCreationResponse

logger = logging.getLogger(__name__)


class BaseGitlabVersionPublisherException(BaseGitVersionPublisherError):
    """ Base exception for :class:`MergeVersionPublisher`. """


class NullablePullRequestUrlError(BaseGitlabVersionPublisherException):
    """ Exception for nullable merge-request in selected Draft. """


class GitlabVersionPublisher(GitVersionPublisher):
    """ Class for feature version's merge requests management relative to Atlassian Gitlab API. """

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        project_settings: OverhaveProjectSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        test_run_storage: ITestRunStorage,
        draft_storage: IDraftStorage,
        file_manager: FileManager,
        gitlab_publisher_settings: OverhaveGitlabPublisherSettings,
        client: GitlabHttpClient,
    ):
        super().__init__(
            file_settings=file_settings,
            project_settings=project_settings,
            feature_storage=feature_storage,
            scenario_storage=scenario_storage,
            test_run_storage=test_run_storage,
            draft_storage=draft_storage,
            file_manager=file_manager,
        )
        self._gitlab_publisher_settings = gitlab_publisher_settings
        self._client = client

    def _save_as_duplicate(self, context: PublisherContext) -> None:
        previous_draft = self._draft_storage.get_previous_feature_draft(context.feature.id)
        if previous_draft.pr_url is None:
            raise NullablePullRequestUrlError(
                "Previous draft with id=%s has not got merge-request URL!", previous_draft.id
            )
        if previous_draft.published_at is None:
            raise RuntimeError
        self._draft_storage.save_response(
            draft_id=context.draft.id,
            pr_url=previous_draft.pr_url,
            published_at=previous_draft.published_at,
            opened=True,
        )

    def publish_version(self, draft_id: int) -> None:
        logger.info("Start processing draft_id=%s...", draft_id)
        context = self._push_version(draft_id)
        if not isinstance(context, PublisherContext):
            return
        merge_request = GitlabMrRequest(
            title=context.feature.name,
            description=self._compile_publication_description(context),
            open=True,
            fromRef=GitlabBranch(id=context.target_branch, repository=self._gitlab_publisher_settings.repository),
            toRef=self._gitlab_publisher_settings.target_branch,
            reviewers=self._gitlab_publisher_settings.get_reviewers(feature_type=context.feature.feature_type.name),
        )
        logger.info("Prepared pull-request: %s", merge_request.json(by_alias=True))
        try:
            response = self._client.send_merge_request(merge_request)
            if isinstance(response, GitlabMrCreationResponse):
                self._draft_storage.save_response(
                    draft_id=draft_id,
                    pr_url=response.get_mr_url(),
                    published_at=response.created_at,
                    opened=response.state == "opened",
                )
                return
            if isinstance(response, GitlabErrorResponse) and response.duplicate:
                self._save_as_duplicate(context)
                return
            logger.error("Gotten error response from Gitlab: %s", response)
        except GitlabHttpClientConflictError:
            logger.exception("Gotten conflict. Try to return last merge-request for Draft with id=%s...", draft_id)
            self._save_as_duplicate(context)
        except HTTPError:
            logger.exception("Got HTTP error while trying to sent merge-request!")
