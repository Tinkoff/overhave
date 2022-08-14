from typing import Optional
from unittest import mock

import allure
import py
import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from demo.settings import OverhaveDemoAppLanguage
from overhave import (
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveProjectSettings,
    OverhaveScenarioCompilerSettings,
    OverhaveScenarioParserSettings,
)
from overhave.entities import FeatureExtractor
from overhave.scenario import FileManager, ScenarioCompiler, ScenarioParser
from overhave.storage import FeatureModel, FeatureTypeModel, ScenarioModel, TagModel, TestExecutorContext, TestRunModel
from overhave.utils import get_current_time
from tests.objects import get_test_feature_containers, get_test_feature_extractor


@pytest.fixture()
def test_scenario_text(request: FixtureRequest, language_settings: OverhaveLanguageSettings) -> str:
    if hasattr(request, "param"):
        return str(request.param)  # type: ignore
    features = get_test_feature_containers()
    if language_settings.step_prefixes is None:
        lang = OverhaveDemoAppLanguage.EN
    else:
        lang = OverhaveDemoAppLanguage.RU
    return next(
        iter(
            feature.scenario for feature in features if feature.language is lang and feature.name.startswith("scenario")
        )
    )


@pytest.fixture()
def test_feature() -> FeatureModel:
    return FeatureModel(
        id=1,
        name="feature",
        author="keks",
        type_id=1,
        task=["OVERHAVE-1"],
        last_edited_by="overlord",
        last_edited_at=get_current_time(),
        released=False,
        feature_type=FeatureTypeModel(id=1, name=get_test_feature_extractor().feature_types[0]),
        feature_tags=[
            TagModel(id=1, value="tag1", created_by="qqq", created_at=get_current_time()),
            TagModel(id=2, value="tag2", created_by="qqq", created_at=get_current_time()),
        ],
        file_path="my_folder/my_feature",
        severity=allure.severity_level.NORMAL,
    )


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


@pytest.fixture()
def test_scenario(test_scenario_text: str, faker: Faker) -> ScenarioModel:
    return ScenarioModel(id=faker.random_int(), feature_id=faker.random_int(), text=test_scenario_text)


@pytest.fixture()
def test_executor_ctx(
    test_feature: FeatureModel, test_scenario: ScenarioModel, test_testrun: TestRunModel
) -> TestExecutorContext:
    return TestExecutorContext(feature=test_feature, scenario=test_scenario, test_run=test_testrun)


@pytest.fixture()
def test_scenario_compiler(
    language_settings: OverhaveLanguageSettings,
    test_compilation_settings: OverhaveScenarioCompilerSettings,
    tasks_keyword: Optional[str],
) -> ScenarioCompiler:
    return ScenarioCompiler(
        compilation_settings=test_compilation_settings,
        language_settings=language_settings,
        tasks_keyword=tasks_keyword,
    )


@pytest.fixture()
def test_scenario_parser(
    test_parser_settings: OverhaveScenarioParserSettings,
    test_compilation_settings: OverhaveScenarioCompilerSettings,
    language_settings: OverhaveLanguageSettings,
    tasks_keyword: Optional[str],
) -> ScenarioParser:
    return ScenarioParser(
        parser_settings=test_parser_settings,
        compilation_settings=test_compilation_settings,
        language_settings=language_settings,
        feature_extractor=get_test_feature_extractor(),
        tasks_keyword=tasks_keyword,
    )


@pytest.fixture()
def test_file_settings(tmpdir: py.path.local) -> OverhaveFileSettings:
    settings = OverhaveFileSettings(work_dir=tmpdir, root_dir=tmpdir, tmp_dir=tmpdir / "tmp")
    settings.tmp_features_dir.mkdir(parents=True)
    settings.tmp_fixtures_dir.mkdir(parents=True)
    return settings


@pytest.fixture()
def test_file_manager(
    test_project_settings: OverhaveProjectSettings,
    test_file_settings: OverhaveFileSettings,
    test_scenario_compiler: ScenarioCompiler,
) -> FileManager:
    return FileManager(
        project_settings=test_project_settings,
        file_settings=test_file_settings,
        feature_extractor=get_test_feature_extractor(),
        scenario_compiler=test_scenario_compiler,
    )


@pytest.fixture()
def test_tmp_feature_file(faker: Faker) -> mock.MagicMock:
    feature_file_mock = mock.MagicMock()
    feature_file_mock.name = faker.word()
    return feature_file_mock


@pytest.fixture()
def mocked_feature_extractor(test_file_settings: OverhaveFileSettings) -> FeatureExtractor:
    extractor_mock = mock.MagicMock()
    extractor_mock.feature_type_to_dir_mapping = {
        feature_type: test_file_settings.features_dir / feature_type
        for feature_type, path in get_test_feature_extractor().feature_type_to_dir_mapping.items()
    }
    return extractor_mock


@pytest.fixture()
def test_file_manager_with_mocked_extractor(
    test_file_manager: FileManager,
    mocked_feature_extractor: FeatureExtractor,
) -> FileManager:
    test_file_manager._feature_extractor = mocked_feature_extractor
    return test_file_manager
