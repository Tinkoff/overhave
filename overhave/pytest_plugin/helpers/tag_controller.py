import re
from functools import cached_property
from typing import Mapping, Optional, Pattern

import allure_commons.types
import pytest
from _pytest.mark.structures import MarkDecorator
from pydantic import BaseModel


class TagParsingModel(BaseModel):
    """Class for tag parsing info."""

    tag_pattern: Pattern[str]
    mark_decorator: MarkDecorator
    link_type: str

    class Config:
        arbitrary_types_allowed = True


class TagEvaluationResult(BaseModel):
    """Class for tag evaluation result."""

    marker: MarkDecorator
    url: Optional[str]
    link_type: str

    class Config:
        arbitrary_types_allowed = True


class BaseOverhaveTagControllerException(Exception):
    """Base exception for :class:`OverhaveTagController`."""


class NoReasonForMarkDecoratorError(Exception):
    """Exception for situation with nullable reason in tag."""


class OverhaveTagController:
    """Class for mark decorators setup via special Overhave tags."""

    @staticmethod
    def _get_tag_pattern(keyword: str) -> Pattern[str]:
        return re.compile(rf"\b({keyword})+(\(+[^@()]+\)+)?\b")

    @cached_property
    def _tag_to_parsing_model_mapping(self) -> Mapping[str, TagParsingModel]:
        return {
            "disabled": TagParsingModel(
                tag_pattern=self._get_tag_pattern("disabled"),
                mark_decorator=pytest.mark.skip,
                link_type=allure_commons.types.LinkType.LINK,
            ),
            "xfail": TagParsingModel(
                tag_pattern=self._get_tag_pattern("xfail"),
                mark_decorator=pytest.mark.xfail,
                link_type=allure_commons.types.LinkType.ISSUE,
            ),
        }

    @cached_property
    def _reason_pattern(self) -> Pattern[str]:
        return re.compile(r"\w+\((?P<reason>[^@()]+)\)")

    @cached_property
    def _url_pattern(self) -> Pattern[str]:
        return re.compile(r"(?P<url>\b\w+://[^\s\"\']+\b)")

    def _get_url(self, reason: str) -> Optional[str]:
        searched = self._url_pattern.search(reason)
        if searched is not None:
            return searched.group("url")
        return None

    def get_suitable_parsing_model(self, name: str) -> Optional[TagParsingModel]:
        for parsing_model in self._tag_to_parsing_model_mapping.values():
            result = parsing_model.tag_pattern.match(name)
            if result is not None:
                return parsing_model
        return None

    def evaluate_tag(self, name: str, parsing_model: TagParsingModel) -> TagEvaluationResult:
        reason_error = NoReasonForMarkDecoratorError(
            f"Tag '{name}' has been used without reason! Please, setup reason using round brackets `(`, `)`\n"
            "For example: `@disabled(TODO: https://tracker.mydomain.com/browse/PRJ-333)`"
        )
        match = self._reason_pattern.match(name)
        if match is None:
            raise reason_error
        reason = match.group("reason")
        if reason is None:
            raise reason_error
        kwargs = {"reason": reason}
        return TagEvaluationResult(
            marker=parsing_model.mark_decorator(**kwargs), url=self._get_url(reason), link_type=parsing_model.link_type
        )
