import logging
from http import HTTPStatus

import httpx
from gitlab import GitlabError

from overhave import db
from overhave.entities import GitRepositoryInitializer
from overhave.metrics import PublicationOverhaveMetricContainer
from overhave.publication.git_publisher import GitVersionPublisher
from overhave.publication.gitlab.settings import OverhaveGitlabPublisherSettings
from overhave.publication.gitlab.tokenizer.client import TokenizerClient
from overhave.scenario import FileManager, OverhaveProjectSettings
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
from overhave.transport.http.gitlab_client import GitlabHttpClient, GitlabMrRequest

logger = logging.getLogger(__name__)


class GitlabVersionPublisher(GitVersionPublisher[OverhaveGitlabPublisherSettings]):
    """Class for feature version's merge requests management relative to Gitlab API."""

    def __init__(
        self,
        project_settings: OverhaveProjectSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        test_run_storage: ITestRunStorage,
        draft_storage: IDraftStorage,
        file_manager: FileManager,
        git_initializer: GitRepositoryInitializer,
        gitlab_publisher_settings: OverhaveGitlabPublisherSettings,
        gitlab_client: GitlabHttpClient,
        tokenizer_client: TokenizerClient,
        metric_container: PublicationOverhaveMetricContainer,
    ):
        super().__init__(
            project_settings=project_settings,
            feature_storage=feature_storage,
            scenario_storage=scenario_storage,
            test_run_storage=test_run_storage,
            draft_storage=draft_storage,
            file_manager=file_manager,
            git_initializer=git_initializer,
            git_publisher_settings=gitlab_publisher_settings,
            metric_container=metric_container,
        )
        self._gitlab_client = gitlab_client
        self._tokenizer_client = tokenizer_client

    def publish_version(self, draft_id: int) -> db.DraftStatus:
        context = self._prepare_publisher_context(draft_id)
        if context is None:
            self._draft_storage.set_draft_status(draft_id=draft_id, status=db.DraftStatus.INTERNAL_ERROR)
            return db.DraftStatus.INTERNAL_ERROR
        merge_request = GitlabMrRequest(
            project_id=self._git_publisher_settings.repository_id,
            title=context.feature.name,
            source_branch=context.target_branch,
            target_branch=self._git_publisher_settings.target_branch,
            description=self._compile_publication_description(context),
            reviewer_ids=self._git_publisher_settings.get_reviewers(feature_type=context.feature.feature_type.name),
        )
        logger.info("Prepared merge-request: %s", merge_request.model_dump_json(by_alias=True))
        try:
            token = (
                self._gitlab_client._settings.auth_token or self._tokenizer_client.get_token(draft_id=draft_id).token
            )
            response = self._gitlab_client.send_merge_request(
                merge_request=merge_request, token=token, repository_id=self._git_publisher_settings.repository_id
            )
            self._draft_storage.save_response_as_created(
                draft_id=draft_id,
                pr_url=response.web_url,
                published_at=response.created_at,
            )
            logger.info("Draft.id=%s successfully sent to GitLab", draft_id)
            return db.DraftStatus.CREATED
        except (GitlabError, httpx.HTTPError) as err:
            logger.exception("Got error while trying to sent merge-request!")
            if isinstance(err, GitlabError) and err.response_code == HTTPStatus.CONFLICT:
                self._draft_storage.save_response_as_duplicate(
                    draft_id=context.draft.id, feature_id=context.feature.id, traceback=str(err)
                )
                return db.DraftStatus.DUPLICATE
            self._draft_storage.set_draft_status(
                draft_id=draft_id, status=db.DraftStatus.INTERNAL_ERROR, traceback=str(err)
            )
            return db.DraftStatus.INTERNAL_ERROR
