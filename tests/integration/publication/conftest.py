from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockFixture

from overhave import OverhaveFileSettings, OverhaveProjectSettings
from overhave.entities import GitRepositoryInitializer
from overhave.publication import GitlabVersionPublisher, TokenizerClient, StashVersionPublisher
from overhave.transport import GitlabHttpClient, StashHttpClient


@pytest.fixture()
def gitlab_version_publisher(mocker: MockFixture) -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        project_settings=mocked_project_settings,
        feature_storage=,
        scenario_storage=,
        test_run_storage=,
        draft_storage=,
        file_manager=,
        git_initializer=mocked_git_initializer,
        gitlab_publisher_settings=mocked_gitlab_publisher_settings,
        gitlab_client=mocked_gitlab_client,
        tokenizer_client=mocked_tokenizer_client,
    )

@pytest.fixture()
def stash_version_publisher(mocker: MockFixture) -> StashVersionPublisher:
    return StashVersionPublisher(
        project_settings=mocked_project_settings,
        feature_storage=,
        scenario_storage=,
        test_run_storage=,
        draft_storage=,
        file_manager=,
        git_initializer=mocked_git_initializer,
        stash_publisher_settings=mocked_stash_publisher_settings,
        stash_client=mocked_stash_client,
    )

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
def mocked_stash_client(mocker: MockFixture) -> StashHttpClient:
    return cast(StashHttpClient, mocker.create_autospec(StashHttpClient))

@pytest.fixture()
def mocked_gitlab_client(mocker: MockFixture) -> GitlabHttpClient:
    return cast(GitlabHttpClient, mocker.create_autospec(GitlabHttpClient))

@pytest.fixture()
def mocked_tokenizer_client(mocker: MockFixture) -> TokenizerClient:
    return cast(TokenizerClient, mocker.create_autospec(TokenizerClient))

@pytest.fixture()
def test_file_settings(request: FixtureRequest) -> OverhaveFileSettings:
    if hasattr(request, "param"):
        return cast(OverhaveFileSettings, request.param)
    raise NotImplementedError

@pytest.fixture()
def mocked_git_initializer(mocker: MockFixture) -> GitRepositoryInitializer:
    return cast(GitRepositoryInitializer, mocker.create_autospec(GitRepositoryInitializer))
