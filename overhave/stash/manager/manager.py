import logging
from typing import Optional

import git

from overhave.entities.converters import ProcessingContext, get_context_by_test_run_id
from overhave.entities.settings import OverhaveFileSettings
from overhave.scenario import FileManager, generate_task_info
from overhave.stash.client import StashClient
from overhave.stash.errors import StashPrCreationError, StashValidationError
from overhave.stash.manager.abstract import IStashProjectManager
from overhave.stash.models import StashBranch, StashErrorResponse, StashPrCreationResponse, StashPrRequest
from overhave.stash.settings import OverhaveStashProjectSettings
from overhave.storage.pull_request import get_last_pr_url
from overhave.utils.time import get_current_time

logger = logging.getLogger(__name__)


class StashCommonMixin:
    """ Mixin for :class:`StashProjectManager`. """

    @staticmethod
    def _create_head(name: str, repository: git.Repo) -> git.Head:
        origin: git.Head = repository.remotes.origin
        try:
            origin.pull()
        except git.GitCommandError as e:
            raise RuntimeError from e

        logger.info("Origin successfully pulled")
        if name in repository.heads:
            repository.delete_head(repository.heads[name], force=True)
            logger.warning("Trashed existed branch with name '%s'", name)

        branch = repository.create_head(name)
        logger.info("Created head for branch: %s", branch)
        assert repository.active_branch != branch
        return branch

    @staticmethod
    def _make_compatible_str(input_str: str) -> str:
        return input_str.lower().replace(" ", "_")

    @staticmethod
    def _generate_response(
        title: str, pr_url: Optional[str] = None, traceback: Optional[Exception] = None
    ) -> StashPrCreationResponse:
        return StashPrCreationResponse(
            title=title,
            open=False,
            traceback=traceback,
            createdDate=get_current_time(),
            updatedDate=get_current_time(),
            pull_request_url=pr_url,
        )


class StashProjectManager(StashCommonMixin, IStashProjectManager):
    """ Class for feature pull requests management. """

    def __init__(
        self,
        stash_project_settings: OverhaveStashProjectSettings,
        file_settings: OverhaveFileSettings,
        client: StashClient,
        file_manager: FileManager,
        task_links_keyword: Optional[str],
    ):
        self._stash_project_settings = stash_project_settings
        self._file_settings = file_settings
        self._client = client
        self._file_manager = file_manager
        self._task_links_keyword = task_links_keyword

    def _make_description(self, context: ProcessingContext) -> str:
        return "\n".join(
            (
                f"Feature ID: {context.feature.id}. Type: '{context.feature.feature_type.name}'.",
                f"Created by: @{context.feature.author} at {context.feature.created_at}.",
                f"Last edited by: @{context.feature.last_edited_by}.",
                generate_task_info(tasks=context.feature.task, header=self._task_links_keyword),
                f"PR from Test Run ID: {context.test_run.id}. Executed by: @{context.test_run.executed_by}",
            )
        )

    def _create_commit(self, context: ProcessingContext, repository: git.Repo, branch: git.Head) -> None:
        original_branch = repository.active_branch
        changes_pushed = False
        try:
            branch.checkout()
            logger.info("Active branch after checkout: %s", repository.active_branch)
            # Раньше было self._path_settings.bdd_chat_features_dir
            feature_file = self._file_manager.produce_feature_file(context=context)
            logger.info("Untracked files after feature creation: %s", repository.untracked_files)
            repository.index.add([feature_file.as_posix()])
            logger.info("Untracked files after index update: %s", repository.untracked_files)

            repository.index.commit(
                (
                    f"Added feature {context.feature.name} "
                    f"(id {context.feature.id}) "
                    f"by {context.test_run.executed_by}"
                ),
                skip_hooks=True,
            )
            logger.info("Commit successfully created")
            assert (
                repository.active_branch != original_branch
            ), f"Current branch could not be equal to '{original_branch}'!"
            assert repository.active_branch == branch, f"Current branch should be equal to '{branch}'!"

            logger.info("Remote origin url: %s", repository.remotes.origin.url)
            repository.git.push("origin", branch, force=True)
            logger.info("Changes successfully pushed to remote repository")
            changes_pushed = True
        except (git.GitCommandError, AssertionError):
            logger.exception("Error while trying to commit feature file!")

        if original_branch != repository.active_branch:
            logger.info("Current branch is '%s'", repository.active_branch)
            original_branch.checkout()
            logger.info("Branch returned to '%s'", repository.active_branch)

        if not changes_pushed:
            raise RuntimeError("Commit has not been created!")

    def create_pull_request(self, test_run_id: int) -> StashPrCreationResponse:
        ctx = get_context_by_test_run_id(test_run_id)

        repository = git.Repo(self._file_settings.features_base_dir)
        logger.info("Repository: %s", repository)
        logger.info("Working dir: %s", repository.working_dir)
        logger.info("Active head: %s", repository.active_branch)

        branch_name = f"bdd-feature-{ctx.feature.id}"
        try:
            branch = self._create_head(name=branch_name, repository=repository)
            self._create_commit(context=ctx, repository=repository, branch=branch)
        except RuntimeError as e:
            logger.exception('Error while trying to commit code!')
            return self._generate_response(title=ctx.feature.name, traceback=e)

        pull_request = StashPrRequest(
            title=f"BDD {ctx.feature.name}",
            description=self._make_description(ctx),
            open=True,
            fromRef=StashBranch(id=branch_name, repository=self._stash_project_settings.repository),
            toRef=self._stash_project_settings.target_branch,
            reviewers=self._stash_project_settings.get_reviewers(feature_type=ctx.feature.feature_type.name),
        )
        logger.info('Prepared PR: %s', pull_request.json(by_alias=True))
        try:
            response = self._client.send_pr(pull_request)
            if isinstance(response, StashPrCreationResponse):
                return response
            if isinstance(response, StashErrorResponse) and response.duplicate:
                return self._generate_response(
                    title=pull_request.title or ctx.feature.name, pr_url=get_last_pr_url(feature_id=ctx.feature.id)
                )
            raise StashPrCreationError(response)
        except StashValidationError as e:
            logger.exception("PR has not been created in Stash repository!")
            fake_response = self._generate_response(title=pull_request.title, traceback=e)  # type: ignore
            logger.warning("Created fail response: %s", fake_response)
            return fake_response
