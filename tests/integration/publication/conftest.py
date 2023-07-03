import datetime
from http import HTTPStatus
from typing import cast

import allure
import faker
import httpx
import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from gitlab import GitlabError
from pytest_mock import MockFixture
from requests_mock import request

from overhave import OverhaveProjectSettings, OverhaveGitlabPublisherSettings
from overhave.entities import GitRepositoryInitializer
from overhave.publication import GitlabVersionPublisher, TokenizerClient, StashVersionPublisher
from overhave.publication.gitlab.tokenizer.client import TokenizerResponse
from overhave.scenario import FileManager
from overhave.storage import FeatureModel, ScenarioModel, TestRunModel, TagModel, FeatureTypeModel, PublisherContext, \
    DraftModel
from overhave.transport import GitlabHttpClient, StashHttpClient, GitlabMrCreationResponse
from overhave.utils import get_current_time
from tests.integration.conftest import test_run_storage, test_scenario_storage, test_feature_storage, \
    test_draft_storage, test_draft


@pytest.fixture()
def gitlab_version_publisher(
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
    request: FixtureRequest,
    test_feature: FeatureModel,
    test_scenario: ScenarioModel,
    test_testrun: TestRunModel,
    test_draft: DraftModel,
) -> GitlabVersionPublisher:
    gitlab_publisher = GitlabVersionPublisher(
        project_settings=test_project_settings,
        feature_storage=test_feature_storage,
        scenario_storage=test_scenario_storage,
        test_run_storage=test_run_storage,
        draft_storage=test_draft_storage,

        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        gitlab_publisher_settings=OverhaveGitlabPublisherSettings(repository_id="123"),
        gitlab_client=mocked_gitlab_client,
        tokenizer_client=mocked_tokenizer_client,
        metric_container=publication_container,
    )
    publisher_context = PublisherContext(
        draft=test_draft,
        target_branch="BQA-0000",
        feature=test_feature,
        scenario=test_scenario,
        test_run=test_testrun,
    )
    gitlab_publisher._prepare_publisher_context = lambda *args: publisher_context
    #if hasattr(request, "param"):
    #    gitlab_publisher._prepare_publisher_context =  lambda *args: None
    return gitlab_publisher

@pytest.fixture()
def stash_version_publisher(publication_container) -> StashVersionPublisher:
    stash_version = StashVersionPublisher(
        project_settings=test_project_settings,
        feature_storage=test_feature_storage,
        scenario_storage=test_scenario_storage,
        test_run_storage=test_run_storage,
        draft_storage=test_draft_storage,

        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        stash_publisher_settings=mocked_stash_publisher_settings,
        stash_client=mocked_stash_client,
    )
    publisher_context = PublisherContext(
        draft=test_draft,
        target_branch="BQA-0000",
        feature=test_feature,
        scenario=test_scenario,
        test_run=test_testrun,
    )
    stash_version._prepare_publisher_context.side_effect = publisher_context
    if hasattr(request, "param"):
        stash_version._prepare_publisher_context.side_effect = None
    return stash_version


@pytest.fixture()
def test_project_settings() -> OverhaveProjectSettings:
    return OverhaveProjectSettings(
        task_tracker_url="http://task_tracker_url.com", tasks_keyword="tasks_keyword", git_project_url="http://task_tracker_url.com"
    )


@pytest.fixture()
def mocked_file_manager(mocker: MockFixture) -> FileManager:
    return cast(FileManager, mocker.create_autospec(FileManager))


@pytest.fixture()
def mocked_stash_publisher_settings(mocker: MockFixture) -> OverhaveProjectSettings:
    return cast(OverhaveProjectSettings, mocker.create_autospec(OverhaveProjectSettings))

@pytest.fixture()
def mocked_git_initializer(mocker: MockFixture) -> GitRepositoryInitializer:
    return cast(GitRepositoryInitializer, mocker.create_autospec(GitRepositoryInitializer))

@pytest.fixture()
def should_raise_gitlab(request: FixtureRequest)-> bool:
    if hasattr(request, "param"):
        return True
    return False


@pytest.fixture()
def mocked_gitlab_client(mocker: MockFixture, should_raise_gitlab: bool) -> GitlabHttpClient:
    client = mocker.create_autospec(GitlabHttpClient)
    client.send_merge_request.return_value = GitlabMrCreationResponse(created_at=get_current_time(), web_url="hehe")
    if should_raise_gitlab:
        gitlab_error = GitlabError(response_code=HTTPStatus.CONFLICT)
        client.send_merge_request.return_value = gitlab_error
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
        client.get_token.side_effect = httpx.HTTPError
    return client

@pytest.fixture()
def mocked_stash_client(mocker: MockFixture) -> StashHttpClient:
    client = mocker.create_autospec(StashHttpClient)
    return client

@pytest.fixture()
def test_testrun() -> TestRunModel:
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