from http import HTTPStatus
from typing import cast

import httpx
import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from gitlab import GitlabError
from pytest_mock import MockFixture

from overhave import (
    OverhaveGitlabClientSettings,
    OverhaveGitlabPublisherSettings,
    OverhaveProjectSettings,
    OverhaveStashPublisherSettings,
)
from overhave.entities import GitRepositoryInitializer
from overhave.publication import GitlabVersionPublisher, StashVersionPublisher, TokenizerClient
from overhave.publication.gitlab.tokenizer.client import TokenizerResponse
from overhave.scenario import FileManager
from overhave.storage import PublisherContext, TestRunModel
from overhave.transport import GitlabHttpClient, GitlabMrCreationResponse, StashHttpClient
from overhave.utils import get_current_time


@pytest.fixture()
def gitlab_version_publisher(
    simple_gitlab_version_publisher,
    publisher_context,
) -> GitlabVersionPublisher:
    simple_gitlab_version_publisher._prepare_publisher_context = lambda *args: publisher_context
    return simple_gitlab_version_publisher


@pytest.fixture()
def gitlab_version_publisher_without_context(
    simple_gitlab_version_publisher, publisher_context
) -> GitlabVersionPublisher:
    simple_gitlab_version_publisher._prepare_publisher_context = lambda *args: None
    return simple_gitlab_version_publisher


@pytest.fixture()
def simple_gitlab_version_publisher(
    test_project_settings,
    test_feature_storage,
    test_scenario_storage,
    test_run_storage,
    test_draft_storage,
    mocked_file_manager,
    mocked_git_initializer,
    mocked_gitlab_client,
    mocked_tokenizer_client,
    publication_container,
    test_gitlab_publisher_settings,
) -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        project_settings=test_project_settings,
        feature_storage=test_feature_storage,
        scenario_storage=test_scenario_storage,
        test_run_storage=test_run_storage,
        draft_storage=test_draft_storage,
        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        gitlab_publisher_settings=test_gitlab_publisher_settings,
        gitlab_client=mocked_gitlab_client,
        tokenizer_client=mocked_tokenizer_client,
        metric_container=publication_container,
    )


@pytest.fixture()
def stash_version_publisher(
    simple_stash_version_publisher,
    request,
    publisher_context,
) -> StashVersionPublisher:
    simple_stash_version_publisher._prepare_publisher_context = lambda *args: publisher_context
    return simple_stash_version_publisher


@pytest.fixture()
def stash_version_publisher_without_context(simple_stash_version_publisher) -> StashVersionPublisher:
    simple_stash_version_publisher._prepare_publisher_context = lambda *args: None
    return simple_stash_version_publisher


@pytest.fixture()
def simple_stash_version_publisher(
    test_project_settings,
    test_feature_storage,
    test_scenario_storage,
    test_run_storage,
    test_draft_storage,
    mocked_file_manager,
    mocked_git_initializer,
    mocked_stash_client,
    publication_container,
    test_stash_publisher_settings,
) -> StashVersionPublisher:
    return StashVersionPublisher(
        project_settings=test_project_settings,
        feature_storage=test_feature_storage,
        scenario_storage=test_scenario_storage,
        test_run_storage=test_run_storage,
        draft_storage=test_draft_storage,
        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        stash_publisher_settings=test_stash_publisher_settings,
        stash_client=mocked_stash_client,
        metric_container=publication_container,
    )


@pytest.fixture()
def test_project_settings() -> OverhaveProjectSettings:
    return OverhaveProjectSettings(
        task_tracker_url="http://task_tracker_url.com",
        tasks_keyword="tasks_keyword",
        git_project_url="http://task_tracker_url.com",
    )


@pytest.fixture()
def test_gitlab_publisher_settings() -> OverhaveGitlabPublisherSettings:
    return OverhaveGitlabPublisherSettings(repository_id="123")


@pytest.fixture()
def test_stash_publisher_settings() -> OverhaveStashPublisherSettings:
    return OverhaveStashPublisherSettings(repository_name="bdd-lolkek", project_key="LOL")


@pytest.fixture()
def mocked_file_manager(mocker: MockFixture) -> FileManager:
    return cast(FileManager, mocker.create_autospec(FileManager))


@pytest.fixture()
def publisher_context(
    test_feature,
    test_scenario,
    test_db_test_run,
    test_draft,
) -> PublisherContext:
    return PublisherContext(
        draft=test_draft,
        target_branch="BQA-0000",
        feature=test_feature,
        scenario=test_scenario,
        test_run=test_db_test_run,
    )


@pytest.fixture()
def mocked_git_initializer(mocker: MockFixture) -> GitRepositoryInitializer:
    return cast(GitRepositoryInitializer, mocker.create_autospec(GitRepositoryInitializer))


@pytest.fixture()
def should_raise_gitlab(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return True
    return False


@pytest.fixture()
def mocked_gitlab_client(mocker: MockFixture, should_raise_gitlab: bool, request: FixtureRequest) -> GitlabHttpClient:
    client = mocker.create_autospec(GitlabHttpClient)
    client.configure_mock(_settings=OverhaveGitlabClientSettings(auth_token=None, url="http://task_tracker_url.com"))
    if hasattr(request, "param"):
        client.configure_mock(
            _settings=OverhaveGitlabClientSettings(auth_token="lol_kek", url="http://task_tracker_url.com")
        )
    client.send_merge_request.return_value = GitlabMrCreationResponse(created_at=get_current_time(), web_url="hehe")
    if should_raise_gitlab:
        gitlab_error = GitlabError(response_code=HTTPStatus.CONFLICT)
        client.send_merge_request.side_effect = gitlab_error
    return client


@pytest.fixture()
def should_raise_http(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return True
    return False


@pytest.fixture()
def mocked_tokenizer_client(mocker: MockFixture, should_raise_http: bool, faker: Faker) -> TokenizerClient:
    client = mocker.create_autospec(TokenizerClient)
    client.get_token.return_value = TokenizerResponse(token=faker.word())
    if should_raise_http:
        client.get_token.side_effect = httpx.HTTPError("kek")
    return client


@pytest.fixture()
def mocked_stash_client(mocker: MockFixture) -> StashHttpClient:
    return mocker.create_autospec(StashHttpClient)


@pytest.fixture()
def test_db_test_run() -> TestRunModel:
    return TestRunModel(
        id=1,
        created_at=get_current_time(),
        scenario_id=1,
        name="test",
        start=get_current_time(),
        end=get_current_time(),
        executed_by="executor",
        status="SUCCESS",
        report_status="GENERATION_FAILED",
        report=None,
        traceback=None,
    )
