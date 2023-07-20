import logging

import httpx

from overhave import db
from overhave.entities import GitRepositoryInitializer
from overhave.metrics import PublicationOverhaveMetricContainer
from overhave.publication.git_publisher import GitVersionPublisher
from overhave.publication.stash.settings import OverhaveStashPublisherSettings
from overhave.scenario import FileManager, OverhaveProjectSettings
from overhave.storage import IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
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
        project_settings: OverhaveProjectSettings,
        feature_storage: IFeatureStorage,
        scenario_storage: IScenarioStorage,
        test_run_storage: ITestRunStorage,
        draft_storage: IDraftStorage,
        file_manager: FileManager,
        git_initializer: GitRepositoryInitializer,
        stash_publisher_settings: OverhaveStashPublisherSettings,
        stash_client: StashHttpClient,
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
            git_publisher_settings=stash_publisher_settings,
            metric_container=metric_container,
        )
        self._client = stash_client

    def publish_version(self, draft_id: int) -> db.DraftStatus:
        context = self._prepare_publisher_context(draft_id)
        if context is None:
            self._draft_storage.set_draft_status(draft_id=draft_id, status=db.DraftStatus.INTERNAL_ERROR)
            return db.DraftStatus.INTERNAL_ERROR
        pull_request = StashPrRequest(
            title=context.feature.name,
            description=self._compile_publication_description(context),
            open=True,
            fromRef=StashBranch(id=context.target_branch, repository=self._git_publisher_settings.repository),
            toRef=self._git_publisher_settings.target_branch,
            reviewers=self._git_publisher_settings.get_reviewers(feature_type=context.feature.feature_type.name),
        )
        logger.info("Prepared pull-request: %s", pull_request.model_dump_json(by_alias=True))
        try:
            response = self._client.send_pull_request(pull_request)
            if isinstance(response, StashPrCreationResponse):
                self._draft_storage.save_response_as_created(
                    draft_id=draft_id,
                    pr_url=response.get_pr_url(),
                    published_at=response.created_date,
                )
                return db.DraftStatus.CREATED
            if isinstance(response, StashErrorResponse) and response.duplicate:
                self._draft_storage.save_response_as_duplicate(
                    draft_id=context.draft.id, feature_id=context.feature.id, traceback=None
                )
                return db.DraftStatus.DUPLICATE
            self._draft_storage.set_draft_status(draft_id, db.DraftStatus.INTERNAL_ERROR)
            logger.error("Gotten error response from Stash: %s", response)
            return db.DraftStatus.INTERNAL_ERROR

        except StashHttpClientConflictError as err:
            logger.exception("Gotten conflict. Try to return last pull-request for Draft with id=%s...", draft_id)
            self._draft_storage.save_response_as_duplicate(
                draft_id=context.draft.id, feature_id=context.feature.id, traceback=str(err)
            )
            return db.DraftStatus.DUPLICATE
        except httpx.HTTPError as err:
            self._draft_storage.set_draft_status(draft_id, db.DraftStatus.INTERNAL_ERROR, str(err))
            logger.exception("Got HTTP error while trying to sent pull-request!")
            return db.DraftStatus.INTERNAL_ERROR
