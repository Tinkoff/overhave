import logging

import httpx

from overhave.db import DraftStatus
from overhave.entities import GitRepositoryInitializer, OverhaveFileSettings
from overhave.publication.git_publisher import GitVersionPublisher
from overhave.publication.stash.settings import OverhaveStashPublisherSettings
from overhave.scenario import FileManager, OverhaveProjectSettings
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage, PublisherContext
from overhave.transport import (
    StashBranch,
    StashErrorResponse,
    StashHttpClient,
    StashHttpClientConflictError,
    StashPrCreationResponse,
    StashPrRequest,
)

logger = logging.getLogger(__name__)


class StashVersionPublisher(GitVersionPublisher[OverhaveStashPublisherSettings]):
    """Class for feature version's pull requests management relative to Atlassian Stash API."""

    def __init__(
        self,
        file_settings: OverhaveFileSettings,
        project_settings: OverhaveProjectSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        test_run_storage: ITestRunStorage,
        draft_storage: IDraftStorage,
        file_manager: FileManager,
        git_initializer: GitRepositoryInitializer,
        stash_publisher_settings: OverhaveStashPublisherSettings,
        stash_client: StashHttpClient,
    ):
        super().__init__(
            file_settings=file_settings,
            project_settings=project_settings,
            feature_storage=feature_storage,
            scenario_storage=scenario_storage,
            test_run_storage=test_run_storage,
            draft_storage=draft_storage,
            file_manager=file_manager,
            git_initializer=git_initializer,
        )
        self._stash_publisher_settings = stash_publisher_settings
        self._client = stash_client

    def publish_version(self, draft_id: int) -> None:
        logger.info("Start processing draft_id=%s...", draft_id)
        self._draft_storage.set_draft_status(draft_id, DraftStatus.CREATING)
        context = self._push_version(draft_id)
        if not isinstance(context, PublisherContext):
            return
        pull_request = StashPrRequest(
            title=context.feature.name,
            description=self._compile_publication_description(context),
            open=True,
            fromRef=StashBranch(id=context.target_branch, repository=self._stash_publisher_settings.repository),
            toRef=self._stash_publisher_settings.target_branch,
            reviewers=self._stash_publisher_settings.get_reviewers(feature_type=context.feature.feature_type.name),
        )
        logger.info("Prepared pull-request: %s", pull_request.json(by_alias=True))
        try:
            response = self._client.send_pull_request(pull_request)
            if isinstance(response, StashPrCreationResponse):
                self._draft_storage.save_response(
                    draft_id=draft_id,
                    pr_url=response.get_pr_url(),
                    published_at=response.created_date,
                    status=DraftStatus.CREATED,
                )
                return
            if isinstance(response, StashErrorResponse) and response.duplicate:
                self._save_as_duplicate(context)
                return
            logger.error("Gotten error response from Stash: %s", response)
        except StashHttpClientConflictError:
            logger.exception("Gotten conflict. Try to return last pull-request for Draft with id=%s...", draft_id)
            self._save_as_duplicate(context)
        except httpx.HTTPError as e:
            self._draft_storage.set_draft_status(draft_id, DraftStatus.INTERNAL_ERROR, str(e))
            logger.exception("Got HTTP error while trying to sent pull-request!")
