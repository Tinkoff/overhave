from typing import List, Optional

import pytest

from overhave.entities import FeatureModel, OverhaveLanguageSettings, ScenarioModel, TestExecutorContext
from overhave.extra import RUSSIAN_PREFIXES
from overhave.scenario import IncorrectScenarioTextError, ScenarioCompiler, ScenarioParser, generate_task_info


class TestGenerateTaskInfo:
    """Unit tests for :meth:`generate_task_info`."""

    @pytest.mark.parametrize("tasks", [["EX-1", "EX-2"]])
    @pytest.mark.parametrize("header", ["tasks_header"])
    def test_generate_task_info(self, tasks: List[str], header: str) -> None:
        assert generate_task_info(tasks=tasks, header=header) == f"{header}: {', '.join(tasks)}"

    @pytest.mark.parametrize("tasks", [[]])
    @pytest.mark.parametrize("header", ["tasks_header"])
    def test_generate_task_info_without_tasks(self, tasks: List[str], header: str) -> None:
        assert generate_task_info(tasks=tasks, header=header) == ""

    @pytest.mark.parametrize("tasks", [["EX-1", "EX-2"]])
    @pytest.mark.parametrize("header", [None])
    def test_generate_task_info_without_header(self, tasks: List[str], header: None) -> None:
        assert generate_task_info(tasks=tasks, header=header) == ""


@pytest.mark.parametrize("task_links_keyword", [None, "Tasks"])
@pytest.mark.parametrize(
    "language_settings",
    [OverhaveLanguageSettings(), OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES)],
)
class TestScenarioCompiler:
    """Unit tests for :class:`ScenarioCompiler`."""

    @pytest.mark.parametrize("test_scenario_text", ["Incorrect scenario"], indirect=True)
    def test_compile_scenario_from_incorrect_text(
        self,
        test_scenario_compiler: ScenarioCompiler,
        test_scenario_text: str,
        test_executor_ctx: TestExecutorContext,
    ) -> None:
        with pytest.raises(IncorrectScenarioTextError):
            test_scenario_compiler.compile(context=test_executor_ctx)

    def test_compile_scenario_from_correct_text(
        self,
        task_links_keyword: Optional[str],
        test_scenario_compiler: ScenarioCompiler,
        test_scenario_parser: ScenarioParser,
        test_feature: FeatureModel,
        test_scenario: ScenarioModel,
        test_executor_ctx: TestExecutorContext,
    ) -> None:
        feature_txt = test_scenario_compiler.compile(context=test_executor_ctx)
        parsed_info = test_scenario_parser.parse(feature_txt)
        assert parsed_info.id == test_feature.id
        assert parsed_info.name == test_feature.name
        assert parsed_info.type == test_feature.feature_type.name
        assert parsed_info.tags is not None
        assert set(parsed_info.tags) == {model.value for model in test_feature.feature_tags}
        assert parsed_info.author == test_feature.author
        assert parsed_info.last_edited_by == test_feature.last_edited_by
        assert parsed_info.last_edited_at is not None
        assert parsed_info.last_edited_at.date() == test_feature.last_edited_at.date()
        assert parsed_info.last_edited_at.tzinfo is None
        if task_links_keyword is not None:
            assert parsed_info.tasks == test_feature.task
        else:
            assert parsed_info.tasks is None
        assert parsed_info.scenarios == test_scenario.text
