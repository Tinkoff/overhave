import re
from functools import cached_property
from typing import Mapping, Optional, Pattern, Tuple

import allure_commons.types
import pytest
from _pytest.mark.structures import MarkDecorator
from pydantic import BaseModel


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
    def _tag_to_evaluation_result_mapping(
        self,
    ) -> Mapping[Pattern[str], Tuple[MarkDecorator, allure_commons.types.LinkType]]:
        return {
            self._get_tag_pattern("disabled"): (
                pytest.mark.skip,
                allure_commons.types.LinkType.LINK,
            ),
            self._get_tag_pattern("xfail"): (
                pytest.mark.xfail,
                allure_commons.types.LinkType.ISSUE,
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

    def get_suitable_pattern(self, name: str) -> Optional[Pattern[str]]:
        for pattern in self._tag_to_evaluation_result_mapping:
            result = pattern.match(name)
            if result is not None:
                return pattern
        return None

    def evaluate_tag(self, name: str, pattern: Pattern[str]) -> TagEvaluationResult:
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
        mark_decorator, link_type = self._tag_to_evaluation_result_mapping[pattern]
        return TagEvaluationResult(marker=mark_decorator(**kwargs), url=self._get_url(reason), link_type=link_type)
