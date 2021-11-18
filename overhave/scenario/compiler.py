from typing import List, Optional, cast

from pytest_bdd import types as default_types

from overhave.entities import OverhaveLanguageSettings, OverhaveScenarioCompilerSettings, TestExecutorContext
from overhave.scenario.errors import IncorrectScenarioTextError
from overhave.scenario.mixin import PrefixMixin


def generate_task_info(tasks: List[str], header: Optional[str]) -> str:
    if tasks and header is not None:
        return f"{header}: {', '.join(tasks)}"
    return ""


def generate_tags_list(context: TestExecutorContext) -> Optional[List[str]]:
    if feature_tags := [i.value for i in context.feature.feature_tags]:
        return feature_tags
    return None


class ScenarioCompiler(PrefixMixin):
    """Class for scenario compilation from text view into pytest_bdd feature format."""

    def __init__(
        self,
        compilation_settings: OverhaveScenarioCompilerSettings,
        language_settings: OverhaveLanguageSettings,
        task_links_keyword: Optional[str],
    ):
        self._compilation_settings = compilation_settings
        self._language_settings = language_settings
        self._task_links_keyword = task_links_keyword

    def _get_feature_type_tag(self, scenario_text: str, tag: str) -> str:
        if f"{self._compilation_settings.tag_prefix}{tag}" in scenario_text:
            return ""
        return f"{self._compilation_settings.tag_prefix}{tag}"

    def _get_additional_tags(self, scenario_text: str, tags: Optional[List[str]]) -> str:
        if f"{self._compilation_settings.tag_prefix}{tags}" in scenario_text:
            return ""
        if tags is not None:
            tags_with_prefix = (f"{self._compilation_settings.tag_prefix}{tag}" for tag in tags)
            return f"{' '.join(tags_with_prefix)}"
        return ""

    def _get_feature_prefix_if_specified(self, scenario_text: str) -> Optional[str]:
        keywords: List[str] = [default_types.FEATURE]
        if self._language_settings.step_prefixes is not None:
            keywords.append(self._language_settings.step_prefixes.FEATURE)

        for key in keywords:
            if self._as_prefix(key) not in scenario_text:
                continue
            return key
        return None

    def _detect_feature_prefix_by_scenario_format(self, scenario_text: str) -> str:
        if (
            self._as_prefix(default_types.SCENARIO) in scenario_text
            or self._as_prefix(default_types.SCENARIO_OUTLINE) in scenario_text
        ):
            return cast(str, default_types.FEATURE)
        step_prefixes = self._language_settings.step_prefixes
        if step_prefixes is not None and (
            self._as_prefix(step_prefixes.SCENARIO) in scenario_text
            or self._as_prefix(step_prefixes.SCENARIO_OUTLINE) in scenario_text
        ):
            return step_prefixes.FEATURE
        raise IncorrectScenarioTextError(
            "Could not find any scenario prefix in scenario text, so could not compile feature header!"
        )

    def _compile_header(self, context: TestExecutorContext) -> str:
        text = context.scenario.text
        feature_prefix = self._get_feature_prefix_if_specified(scenario_text=text)
        if not feature_prefix:
            feature_prefix = self._detect_feature_prefix_by_scenario_format(scenario_text=text)
        blocks_delimiter = f" {self._compilation_settings.blocks_delimiter} "
        if context.test_run.start is None:
            raise RuntimeError
        return "\n".join(
            (
                f"{self._get_feature_type_tag(scenario_text=text, tag=context.feature.feature_type.name)} "
                f"{self._get_additional_tags(scenario_text=text, tags=generate_tags_list(context))}",
                f"{self._as_prefix(feature_prefix)} {context.feature.name}",
                f"{self._compilation_settings.id_prefix} {context.feature.id}",
                (
                    f"{self._compilation_settings.created_by_prefix} {context.feature.author}"
                    f"{blocks_delimiter}"
                    f"{self._compilation_settings.last_edited_by_prefix} {context.feature.last_edited_by}"
                    f"{self._compilation_settings.time_delimiter} "
                    f"{context.feature.last_edited_at.strftime(self._compilation_settings.time_format)}"
                    f"{blocks_delimiter}"
                    f"{self._compilation_settings.published_by_prefix} {context.test_run.executed_by}"
                ),
                generate_task_info(tasks=context.feature.task, header=self._task_links_keyword),
                "",
            )
        )

    def compile(self, context: TestExecutorContext) -> str:
        return self._compile_header(context=context) + "\n" + context.scenario.text.strip("\n") + "\n"
