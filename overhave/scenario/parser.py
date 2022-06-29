import logging
import re
from datetime import datetime
from functools import cached_property
from typing import List, Optional, Sequence

import allure
from pydantic import BaseModel
from pytest_bdd import types as default_types

from overhave.entities import IFeatureExtractor, OverhaveLanguageSettings, OverhaveScenarioCompilerSettings
from overhave.scenario.errors import (
    AdditionalInfoParsingError,
    DatetimeParsingError,
    FeatureNameParsingError,
    FeatureTypeParsingError,
)
from overhave.scenario.mixin import PrefixMixin
from overhave.storage import FeatureTypeName

logger = logging.getLogger(__name__)
_DEFAULT_ID = 1


class FeatureInfo(BaseModel):
    """Model for feature info keeping."""

    id: Optional[int]
    name: Optional[str]
    type: Optional[FeatureTypeName]
    tags: Optional[List[str]]
    severity: Optional[allure.severity_level]
    author: Optional[str]
    last_edited_by: Optional[str]
    last_edited_at: Optional[datetime]
    tasks: Optional[List[str]]
    scenarios: Optional[str]


class ScenarioParser(PrefixMixin):
    """Class for feature files parsing."""

    def __init__(
        self,
        compilation_settings: OverhaveScenarioCompilerSettings,
        language_settings: OverhaveLanguageSettings,
        feature_extractor: IFeatureExtractor,
        tasks_keyword: Optional[str],
    ) -> None:
        self._compilation_settings = compilation_settings
        self._language_settings = language_settings
        self._feature_extractor = feature_extractor
        self._tasks_keyword = tasks_keyword

    @cached_property
    def _feature_prefixes(self) -> List[str]:
        prefixes = [self._as_prefix(default_types.FEATURE)]
        if self._language_settings.step_prefixes is not None:
            prefixes.append(self._as_prefix(self._language_settings.step_prefixes.FEATURE))
        logger.debug("Cached ScenarioParser feature prefixes: %s", prefixes)
        return prefixes

    @cached_property
    def _task_prefix(self) -> Optional[str]:
        if isinstance(self._tasks_keyword, str):
            return self._as_prefix(self._tasks_keyword)
        return None

    def _get_id(self, id_line: str) -> int:
        return int(id_line.removeprefix(self._compilation_settings.id_prefix).strip())

    def _get_name(self, name_line: str, feature_prefix: str) -> str:
        name_parts = name_line.split(feature_prefix)
        if not name_parts:
            raise FeatureNameParsingError(
                f"Could not parse feature name from '{name_line}'!",
            )
        return name_parts[-1].strip()

    def _get_tags(self, tags_line: str) -> List[str]:
        return [tag.strip() for tag in tags_line.split(self._compilation_settings.tag_prefix) if tag]

    def _get_feature_type(self, tags: Sequence[str]) -> FeatureTypeName:
        for tag in tags:
            if tag not in self._feature_extractor.feature_types:
                continue
            return FeatureTypeName(tag)
        raise FeatureTypeParsingError(
            f"Could not get feature type from tags {tags}!",
        )

    def _get_severity_tag(self, tags: Sequence[str]) -> Optional[str]:
        for tag in reversed(tags):
            if self._compilation_settings.severity_keyword not in tag:
                continue
            return tag
        return None

    @staticmethod
    def _get_additional_info(additional_line: str, left_pointer: str, right_pointer: str) -> str:
        result = re.search(rf"({left_pointer})+\s?[\w.]+\s?({right_pointer})+", additional_line)
        if result:
            return result.group(0).removeprefix(left_pointer).removesuffix(right_pointer).strip()
        raise AdditionalInfoParsingError("Could not parse additional info from '%s'!", additional_line)

    def _get_task_info(self, task_line: str) -> List[str]:
        tasks = []
        if self._task_prefix is not None:
            tasks.extend(task_line.removeprefix(self._task_prefix).split(","))
        return [x.strip() for x in tasks]

    def _get_time_info(self, line: str, left_pointer: str, right_pointer: str) -> datetime:
        result = re.search(rf"({left_pointer})+[\w\-:\s]+({right_pointer})+", line)
        if result:
            datetime_str = result.group(0).removeprefix(left_pointer).removesuffix(right_pointer).strip()
            return datetime.strptime(datetime_str, self._compilation_settings.time_format)
        raise DatetimeParsingError("Could not parse datetime from '%s'!", line)

    def _parse_feature_info(self, header: str) -> FeatureInfo:  # noqa: C901
        feature_info = FeatureInfo()
        for line in header.split("\n"):
            if line.startswith(self._compilation_settings.id_prefix):
                feature_info.id = self._get_id(line)
                continue
            if line.startswith(self._compilation_settings.tag_prefix):
                tags = self._get_tags(line)
                feature_info.type = self._get_feature_type(tags)
                tags.remove(feature_info.type)

                severity_tag = self._get_severity_tag(tags)
                if severity_tag is not None:
                    tags.remove(severity_tag)
                    feature_info.severity = allure.severity_level(
                        severity_tag.removeprefix(self._compilation_settings.severity_keyword)
                    )

                feature_info.tags = tags
                continue
            for prefix in self._feature_prefixes:
                if not line.startswith(prefix):
                    continue
                feature_info.name = self._get_name(name_line=line, feature_prefix=prefix)
            if self._compilation_settings.created_by_prefix in line:
                feature_info.author = self._get_additional_info(
                    line,
                    left_pointer=self._compilation_settings.created_by_prefix,
                    right_pointer=self._compilation_settings.blocks_delimiter,
                )
            if self._compilation_settings.last_edited_by_prefix in line:
                feature_info.last_edited_by = self._get_additional_info(
                    line,
                    left_pointer=self._compilation_settings.last_edited_by_prefix,
                    right_pointer=self._compilation_settings.time_delimiter,
                )
                feature_info.last_edited_at = self._get_time_info(
                    line,
                    left_pointer=self._compilation_settings.time_delimiter,
                    right_pointer=self._compilation_settings.blocks_delimiter,
                )
            if self._task_prefix is not None and self._task_prefix in line:
                feature_info.tasks = self._get_task_info(line)
                continue
        if feature_info.name is None:
            raise FeatureNameParsingError(f"Could not parse feature name from header:\n{header}")
        return feature_info

    def parse(self, feature_txt: str) -> FeatureInfo:
        blocks_delimiter = "\n\n"
        indent = "  "
        indent_substitute = "__"
        blocks = [
            block.lstrip(" \n") for block in feature_txt.replace(indent, indent_substitute).split(blocks_delimiter)
        ]
        header = blocks.pop(0)
        feature_info = self._parse_feature_info(header)
        feature_info.scenarios = blocks_delimiter.join(blocks).replace(indent_substitute, indent)
        return feature_info
