import logging
import re
from functools import cached_property
from typing import List, Optional

from pydantic import BaseModel
from pytest_bdd import types as default_types

from overhave.entities import IFeatureExtractor
from overhave.entities.settings import OverhaveLanguageSettings, OverhaveScenarioCompilerSettings
from overhave.scenario.errors import FeatureNameParsingError, FeatureTypeParsingError, LastEditorParsingError
from overhave.scenario.mixin import PrefixMixin

logger = logging.getLogger(__name__)
_DEFAULT_ID = 1


class FeatureInfo(BaseModel):
    """ Model for feature info keeping. """

    name: Optional[str]
    type: Optional[str]
    author: Optional[str]
    last_edited_by: Optional[str]
    tasks: Optional[List[str]]
    scenarios: Optional[str]


class ScenarioParser(PrefixMixin):
    """ Class for feature files parsing. """

    def __init__(
        self,
        compilation_settings: OverhaveScenarioCompilerSettings,
        language_settings: OverhaveLanguageSettings,
        feature_extractor: IFeatureExtractor,
        task_links_keyword: Optional[str],
    ) -> None:
        self._compilation_settings = compilation_settings
        self._language_settings = language_settings
        self._feature_extractor = feature_extractor
        self._task_links_keyword = task_links_keyword

    @cached_property
    def _feature_prefix(self) -> str:
        if self._language_settings.step_prefixes is not None:
            return self._as_prefix(self._language_settings.step_prefixes.FEATURE)
        return self._as_prefix(default_types.FEATURE)

    @cached_property
    def _task_prefix(self) -> Optional[str]:
        if isinstance(self._task_links_keyword, str):
            return self._as_prefix(self._task_links_keyword)
        return None

    def _get_name(self, name_line: str) -> str:
        name_parts = name_line.split(self._feature_prefix)
        if not name_parts:
            raise FeatureNameParsingError(f"Could not parse feature name from '{name_line}'!",)
        return name_parts[-1].strip()

    def _get_feature_type(self, tags_line: str) -> str:
        tags = tags_line.split(self._compilation_settings.tag_prefix)
        for tag in (x.strip() for x in tags if x):
            if tag not in self._feature_extractor.feature_types:
                logger.debug("Unsupported tag: %s%s", self._compilation_settings.tag_prefix, tag)
                continue
            return tag
        raise FeatureTypeParsingError(f"Could not parse feature type from '{tags_line}'!",)

    @staticmethod
    def _get_additional_info(additional_line: str, left_pointer: str, right_pointer: str) -> str:
        result = re.search(rf"({left_pointer})+\s?\w+\s?({right_pointer})+", additional_line)
        if result:
            return result.group(0).lstrip(left_pointer).rstrip(right_pointer).strip()
        raise LastEditorParsingError("Could not parse additional info from '%s'!", additional_line)

    def _get_task_info(self, task_line: str) -> List[str]:
        tasks = task_line.lstrip(self._task_prefix).split(",")
        return [x.strip() for x in tasks]

    def _parse_feature_info(self, header: str) -> FeatureInfo:
        feature_info = FeatureInfo()
        for line in header.split("\n"):
            if line.startswith(self._compilation_settings.tag_prefix):
                feature_info.type = self._get_feature_type(line)
                continue
            if line.startswith(self._feature_prefix):
                feature_info.name = self._get_name(line)
                continue
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
                    right_pointer=self._compilation_settings.last_edited_time_delimiter,
                )
            if self._task_prefix is not None and self._task_prefix in line:
                feature_info.tasks = self._get_task_info(line)
                continue
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
