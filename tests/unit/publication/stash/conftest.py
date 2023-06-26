from typing import Mapping, Sequence, cast

import pytest
from pytest_mock import MockFixture

from overhave import OverhaveFileSettings, OverhaveProjectSettings
from overhave.entities import GitRepositoryInitializer
from overhave.metrics import PublicationOverhaveMetricContainer
from overhave.publication import StashVersionPublisher
from overhave.publication.stash import OverhaveStashPublisherSettings
from overhave.scenario import FileManager
from overhave.storage import FeatureTypeName, IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
from overhave.transport import StashHttpClient


@pytest.fixture()
def test_stash_publisher_settings_with_default_reviewers(
    test_repository_id_or_name: str,
    test_project_key: str,
    test_target_branch: str,
    test_default_reviewers: Sequence[str],
) -> OverhaveStashPublisherSettings:
    return OverhaveStashPublisherSettings(
        repository_name=test_repository_id_or_name,
        project_key=test_project_key,
        default_target_branch_name=test_target_branch,
        default_reviewers=test_default_reviewers,
    )


@pytest.fixture()
def test_stash_project_settings_with_reviewers_mapping(
    test_repository_id_or_name: str,
    test_project_key: str,
    test_target_branch: str,
    test_reviewers_mapping: Mapping[FeatureTypeName, list[str]],
) -> OverhaveStashPublisherSettings:
    return OverhaveStashPublisherSettings(
        repository_name=test_repository_id_or_name,
        project_key=test_project_key,
        default_target_branch_name=test_target_branch,
        feature_type_to_reviewers_mapping=test_reviewers_mapping,
    )


@pytest.fixture()
def mocked_stash_client(mocker: MockFixture) -> StashHttpClient:
    return cast(StashHttpClient, mocker.create_autospec(StashHttpClient))


@pytest.fixture()
def test_stash_publisher_with_default_reviewers(
    test_file_settings: OverhaveFileSettings,
    test_project_settings: OverhaveProjectSettings,
    test_stash_publisher_settings_with_default_reviewers: OverhaveStashPublisherSettings,
    mocked_file_manager: FileManager,
    mocked_git_initializer: GitRepositoryInitializer,
    mocked_stash_client: StashHttpClient,
    publication_container: PublicationOverhaveMetricContainer,
    mocker: MockFixture,
) -> StashVersionPublisher:
    return StashVersionPublisher(
        file_settings=test_file_settings,
        project_settings=test_project_settings,
        feature_storage=mocker.create_autospec(IFeatureStorage),
        scenario_storage=mocker.create_autospec(IScenarioStorage),
        test_run_storage=mocker.create_autospec(ITestRunStorage),
        draft_storage=mocker.create_autospec(IDraftStorage),
        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        stash_publisher_settings=test_stash_publisher_settings_with_default_reviewers,
        stash_client=mocked_stash_client,
        metric_container=publication_container,
    )


@pytest.fixture()
def test_stash_publisher_with_reviewers_mapping(
    test_file_settings: OverhaveFileSettings,
    test_project_settings: OverhaveProjectSettings,
    test_stash_project_settings_with_reviewers_mapping: OverhaveStashPublisherSettings,
    mocked_file_manager: FileManager,
    mocked_git_initializer: GitRepositoryInitializer,
    mocked_stash_client: StashHttpClient,
    publication_container: PublicationOverhaveMetricContainer,
    mocker: MockFixture,
) -> StashVersionPublisher:
    return StashVersionPublisher(
        file_settings=test_file_settings,
        project_settings=test_project_settings,
        feature_storage=mocker.create_autospec(IFeatureStorage),
        scenario_storage=mocker.create_autospec(IScenarioStorage),
        test_run_storage=mocker.create_autospec(ITestRunStorage),
        draft_storage=mocker.create_autospec(IDraftStorage),
        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        stash_publisher_settings=test_stash_project_settings_with_reviewers_mapping,
        stash_client=mocked_stash_client,
        metric_container=publication_container,
    )
