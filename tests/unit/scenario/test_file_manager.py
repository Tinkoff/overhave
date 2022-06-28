from pathlib import Path
from unittest import mock

import pytest

from overhave import OverhaveFileSettings, OverhaveLanguageSettings
from overhave.entities import FeatureExtractor
from overhave.scenario import FileManager, ScenarioCompiler
from overhave.storage import TestExecutorContext
from overhave.test_execution import OverhaveProjectSettings


@pytest.mark.parametrize(
    ("task_tracker_url", "tasks_keyword"),
    [("https://tasktracker.mydomain.com/browse", "Tasks")],
)
@pytest.mark.parametrize("language_settings", [OverhaveLanguageSettings()])
class TestFileManager:
    """Unit tests for :class:`FileManager`."""

    def test_tmp_feature_file(
        self,
        test_file_settings: OverhaveFileSettings,
        test_scenario_compiler: ScenarioCompiler,
        test_executor_ctx: TestExecutorContext,
        test_file_manager: FileManager,
    ) -> None:
        with test_file_manager.tmp_feature_file(test_executor_ctx) as tmp_feature_file:
            file_path = Path(tmp_feature_file.name)
            assert file_path.is_relative_to(test_file_settings.tmp_features_dir)
            assert file_path.read_text() == test_scenario_compiler.compile(test_executor_ctx)

    def test_tmp_fixture_file(
        self,
        test_file_settings: OverhaveFileSettings,
        test_project_settings: OverhaveProjectSettings,
        test_scenario_compiler: ScenarioCompiler,
        test_executor_ctx: TestExecutorContext,
        test_file_manager: FileManager,
        test_tmp_feature_file: mock.MagicMock,
    ) -> None:
        with test_file_manager.tmp_fixture_file(
            context=test_executor_ctx, feature_file=test_tmp_feature_file
        ) as tmp_fixture_file:
            file_path = Path(tmp_fixture_file.name)
            assert file_path.is_relative_to(test_file_settings.tmp_fixtures_dir)
            assert file_path.read_text() == "\n".join(test_project_settings.fixture_content).format(
                feature_file_path=test_tmp_feature_file.name
            )

    def test_produce_feature_file(
        self,
        mocked_feature_extractor: FeatureExtractor,
        test_executor_ctx: TestExecutorContext,
        test_scenario_compiler: ScenarioCompiler,
        test_file_manager_with_mocked_extractor: FileManager,
    ) -> None:
        file_path = test_file_manager_with_mocked_extractor.produce_feature_file(test_executor_ctx)
        feature_dir = mocked_feature_extractor.feature_type_to_dir_mapping[test_executor_ctx.feature.feature_type.name]
        assert file_path == Path(feature_dir) / test_executor_ctx.feature.file_path
        assert file_path.read_text() == test_scenario_compiler.compile(test_executor_ctx)
