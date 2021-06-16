import logging

from requests import HTTPError

from overhave.entities import OverhaveFileSettings, PublisherContext
from overhave.publication.git_publisher import GitVersionPublisher
from overhave.publication.gitlab.settings import OverhaveGitlabPublisherSettings
from overhave.scenario import FileManager
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
from overhave.test_execution import OverhaveProjectSettings
from overhave.transport.http.gitlab_client import GitlabHttpClient, GitlabHttpClientConflictError, GitlabMrRequest
from overhave.transport.http.gitlab_client.models import GitlabBranch, GitlabMrCreationResponse

logger = logging.getLogger(__name__)


class GitlabVersionPublisher(GitVersionPublisher):
    """ Class for feature version's merge requests management relative to Gitlab API. """

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

    def publish_version(self, draft_id: int) -> None:
        logger.info("Start processing draft_id=%s...", draft_id)
        context = self._push_version(draft_id)
        if not isinstance(context, PublisherContext):
            return
        merge_request = GitlabMrRequest(
            project_id=self._gitlab_publisher_settings.repository_id,
            title=context.feature.name,
            description=self._compile_publication_description(context),
            source_branch=GitlabBranch(
                project_id=self._gitlab_publisher_settings.repository.id, branch=context.target_branch
            ),
            target_branch=self._gitlab_publisher_settings.target_branch,
            reviewer_ids=self._gitlab_publisher_settings.get_reviewers(feature_type=context.feature.feature_type.name),
        )
        logger.info("Prepared merge-request: %s", merge_request.json(by_alias=True))
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
        except GitlabHttpClientConflictError:
            logger.exception("Gotten conflict. Try to return last merge-request for Draft with id=%s...", draft_id)
            self._save_as_duplicate(context)
        except HTTPError:
            logger.exception("Got HTTP error while trying to sent merge-request!")
