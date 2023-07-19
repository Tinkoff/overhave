from pathlib import Path
from typing import Callable, cast

import py
import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockerFixture, MockFixture

from overhave import (
    OverhaveAuthorizationStrategy,
    OverhaveFileSettings,
    OverhaveProjectSettings,
    OverhaveScenarioCompilerSettings,
    OverhaveScenarioParserSettings,
)
from overhave.entities import FeatureExtractor, GitRepositoryInitializer
from overhave.factory import IAdminFactory
from overhave.factory.context.base_context import BaseFactoryContext
from overhave.scenario import FileManager


@pytest.fixture()
def mocked_context(session_mocker: MockerFixture, tmpdir: py.path.local) -> BaseFactoryContext:
    context_mock = session_mocker.MagicMock()
    context_mock.auth_settings.auth_strategy = OverhaveAuthorizationStrategy.LDAP
    context_mock.s3_manager_settings.enabled = False
    context_mock.compilation_settings = OverhaveScenarioCompilerSettings()
    context_mock.parser_settings = OverhaveScenarioParserSettings()

    root_dir = Path(tmpdir)
    features_dir = root_dir / "features"
    fixtures_dir = root_dir / "fixtures"
    reports_dir = root_dir / "reports"
    for path in (features_dir, fixtures_dir, reports_dir):
        path.mkdir()
    context_mock.file_settings.tmp_features_dir = features_dir
    context_mock.file_settings.tmp_fixtures_dir = fixtures_dir
    context_mock.file_settings.tmp_reports_dir = reports_dir

    return cast("BaseFactoryContext", context_mock)


@pytest.fixture(scope="session")
def test_compilation_settings() -> OverhaveScenarioCompilerSettings:
    return OverhaveScenarioCompilerSettings()


@pytest.fixture(scope="session")
def test_parser_settings() -> OverhaveScenarioParserSettings:
    return OverhaveScenarioParserSettings()


@pytest.fixture()
def test_file_settings(request: FixtureRequest) -> OverhaveFileSettings:
    if hasattr(request, "param"):
        return cast(OverhaveFileSettings, request.param)
    raise NotImplementedError


@pytest.fixture()
def mocked_file_manager(mocker: MockFixture) -> FileManager:
    return cast(FileManager, mocker.create_autospec(FileManager))


@pytest.fixture()
def mocked_git_initializer(mocker: MockFixture) -> GitRepositoryInitializer:
    return cast(GitRepositoryInitializer, mocker.create_autospec(GitRepositoryInitializer))


@pytest.fixture()
def task_tracker_url(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str | None, request.param)
    return None


@pytest.fixture()
def tasks_keyword(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str, request.param)
    return None


@pytest.fixture()
def git_project_url(request: FixtureRequest) -> str | None:
    if hasattr(request, "param"):
        return cast(str | None, request.param)
    return None


@pytest.fixture()
def test_project_settings(
    task_tracker_url: str | None, tasks_keyword: str | None, git_project_url: str | None
) -> OverhaveProjectSettings:
    return OverhaveProjectSettings(
        task_tracker_url=task_tracker_url, tasks_keyword=tasks_keyword, git_project_url=git_project_url
    )


@pytest.fixture()
def test_feature_extractor(request: FixtureRequest) -> FeatureExtractor:
    if hasattr(request, "param"):
        return cast(FeatureExtractor, request.param)
    raise NotImplementedError


@pytest.fixture()
def patched_admin_factory(
    mocked_context: BaseFactoryContext, clean_admin_factory: Callable[[], IAdminFactory]
) -> IAdminFactory:
    factory = clean_admin_factory()
    factory.set_context(mocked_context)
    return factory
