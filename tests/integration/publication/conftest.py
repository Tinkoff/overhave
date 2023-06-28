import datetime
from typing import cast

import faker
import httpx
import pytest
from _pytest.fixtures import FixtureRequest
from gitlab import GitlabError
from pytest_mock import MockFixture

from overhave import OverhaveProjectSettings
from overhave.entities import GitRepositoryInitializer
from overhave.publication import GitlabVersionPublisher, TokenizerClient, StashVersionPublisher
from overhave.publication.gitlab.tokenizer.client import TokenizerResponse
from overhave.scenario import FileManager
from overhave.transport import GitlabHttpClient, StashHttpClient, GitlabMrCreationResponse
from tests.integration.conftest import test_run_storage, test_scenario_storage, test_feature_storage, test_draft_storage


@pytest.fixture()
def gitlab_version_publisher() -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        project_settings=mocked_project_settings,
        feature_storage=test_feature_storage,
        scenario_storage=test_scenario_storage,
        test_run_storage=test_run_storage,
        draft_storage=test_draft_storage,

        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        gitlab_publisher_settings=mocked_gitlab_publisher_settings,
        gitlab_client=mocked_gitlab_client,
        tokenizer_client=mocked_tokenizer_client,
    )

@pytest.fixture()
def stash_version_publisher() -> StashVersionPublisher:
    return StashVersionPublisher(
        project_settings=mocked_project_settings,
        feature_storage=test_feature_storage,
        scenario_storage=test_scenario_storage,
        test_run_storage=test_run_storage,
        draft_storage=test_draft_storage,

        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        stash_publisher_settings=mocked_stash_publisher_settings,
        stash_client=mocked_stash_client,
    )

@pytest.fixture()
def mocked_file_manager(mocker: MockFixture) -> FileManager:
    return cast(FileManager, mocker.create_autospec(FileManager))

@pytest.fixture()
def mocked_gitlab_publisher_settings(mocker: MockFixture) -> OverhaveProjectSettings:
    return cast(OverhaveProjectSettings, mocker.create_autospec(OverhaveProjectSettings))

@pytest.fixture()
def mocked_stash_publisher_settings(mocker: MockFixture) -> OverhaveProjectSettings:
    return cast(OverhaveProjectSettings, mocker.create_autospec(OverhaveProjectSettings))

@pytest.fixture()
def mocked_project_settings(mocker: MockFixture) -> OverhaveProjectSettings:
    return cast(OverhaveProjectSettings, mocker.create_autospec(OverhaveProjectSettings))

@pytest.fixture()
def mocked_git_initializer(mocker: MockFixture) -> GitRepositoryInitializer:
    return cast(GitRepositoryInitializer, mocker.create_autospec(GitRepositoryInitializer))

@pytest.fixture()
def should_raise_gitlab(request: FixtureRequest)-> bool:
    if hasattr(request, "param"):
        return True
    raise False


@pytest.fixture()
def mocked_gitlab_client(mocker: MockFixture, should_raise_gitlab: bool) -> GitlabHttpClient:
    client = mocker.create_autospec(GitlabHttpClient)
    client.send_merge_request.return_value = GitlabMrCreationResponse(created_at=datetime.date, web_url="hehe")
    if should_raise_gitlab:
        client.send_merge_request.return_value = GitlabError
    return client


@pytest.fixture()
def should_raise_http(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return True
    return False

@pytest.fixture()
def mocked_tokenizer_client(mocker: MockFixture, should_raise_http: bool) -> TokenizerClient:
    client = mocker.create_autospec(TokenizerClient)
    client.get_token.return_value = TokenizerResponse(token=faker.word("fake_token"))
    if should_raise_http:
        client.get_token.side_effect = httpx.HTTPError
    return client

@pytest.fixture()
def mocked_stash_client(mocker: MockFixture) -> StashHttpClient:
    client = mocker.create_autospec(StashHttpClient)
    return client
