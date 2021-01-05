from functools import lru_cache
from typing import List, Optional

import pytest
from _pytest.fixtures import FixtureRequest

from overhave import db
from overhave.entities import (
    OverhaveLanguageSettings,
    OverhaveScenarioCompilerSettings,
    ScenarioCompiler,
    ScenarioParser,
)
from overhave.utils import get_current_time
from tests.objects import get_feature_extractor


@lru_cache(maxsize=None)
def get_feature_types() -> List[str]:
    feature_texts = []
    for value in get_feature_extractor().feature_type_to_dir_mapping.values():
        for item in value.iterdir():
            if item.is_file() and not any((item.name.startswith("."), item.name.startswith("_"))):
                feature_texts.append(item.read_text(encoding="utf-8"))
            continue
    return feature_texts


@lru_cache(maxsize=None)
def get_scenario_texts() -> List[str]:
    scenario_texts = []
    delimiter = "\n\n"
    for feature_text in get_feature_types():
        blocks = feature_text.split(delimiter)
        scenario_texts.append(delimiter.join(blocks[1:]))
    return scenario_texts


@pytest.fixture()
def test_scenario_text(request: FixtureRequest, language_settings: OverhaveLanguageSettings) -> str:
    if hasattr(request, "param"):
        return str(request.param)  # type: ignore
    scenarios = get_scenario_texts()
    if language_settings.step_prefixes is None:
        return scenarios[0]  # english scenario
    return scenarios[1]  # russian scenario


@pytest.fixture()
def test_feature() -> db.FeatureModel:
    return db.FeatureModel(
        id=1,
        name="feature",
        author="keks",
        type_id=1,
        task=["OVERHAVE-1"],
        last_edited_by="overlord",
        released=False,
        feature_type=db.FeatureTypeModel(id=1, name=get_feature_extractor().feature_types[0]),
    )


@pytest.fixture()
def test_testrun() -> db.TestRunModel:
    return db.TestRunModel(
        id=1,
        scenario_id=1,
        name="test",
        start=get_current_time(),
        end=get_current_time(),
        executed_by="executor",
        status="SUCCESS",
        report=None,
        traceback=None,
    )


@pytest.fixture()
def test_scenario(test_scenario_text: str) -> db.ScenarioModel:
    return db.ScenarioModel(id=1, feature_id=1, text=test_scenario_text)


@pytest.fixture()
def test_processing_ctx(
    test_feature: db.FeatureModel, test_scenario: db.ScenarioModel, test_testrun: db.TestRunModel
) -> db.ProcessingContext:
    return db.ProcessingContext(feature=test_feature, scenario=test_scenario, test_run=test_testrun)


@pytest.fixture()
def test_scenario_compiler(
    language_settings: OverhaveLanguageSettings,
    test_compilation_settings: OverhaveScenarioCompilerSettings,
    task_links_keyword: Optional[str],
) -> ScenarioCompiler:
    return ScenarioCompiler(
        compilation_settings=test_compilation_settings,
        language_settings=language_settings,
        task_links_keyword=task_links_keyword,
    )


@pytest.fixture()
def test_scenario_parser(
    test_compilation_settings: OverhaveScenarioCompilerSettings,
    language_settings: OverhaveLanguageSettings,
    task_links_keyword: Optional[str],
) -> ScenarioParser:
    return ScenarioParser(
        compilation_settings=test_compilation_settings,
        language_settings=language_settings,
        feature_extractor=get_feature_extractor(),
        task_links_keyword=task_links_keyword,
    )
