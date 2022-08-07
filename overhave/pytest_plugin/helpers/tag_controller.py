import re
from functools import cached_property
from typing import Mapping, Optional, Pattern

import pytest
from _pytest.mark.structures import MarkDecorator


class BaseOverhaveTagControllerException(Exception):
    """Base exception for :class:`OverhaveTagController`."""


class NotSuitableTagForEvaluationError(Exception):
    """Exception for situation with not suitable tag."""


class NoReasonForMarkDecoratorError(Exception):
    """Exception for situation with nullable reason in tag."""


def _get_tag_pattern(keyword: str) -> Pattern[str]:
    return re.compile(rf"({keyword})+\(?(?P<text>[^@()]+)?\)?")


class OverhaveTagController:
    """Class for mark decorators setup via special Overhave tags."""

    @cached_property
    def _tag_pattern_to_mark_mapping(self) -> Mapping[Pattern[str], MarkDecorator]:
        return {
            _get_tag_pattern("disabled"): pytest.mark.skip,
            _get_tag_pattern("xfail"): pytest.mark.xfail,
        }

    def get_suitable_pattern(self, name: str) -> Optional[Pattern[str]]:
        for pattern in self._tag_pattern_to_mark_mapping:
            result = pattern.match(name)
            if result is not None:
                return pattern
        return None

    def evaluate_tag(self, name: str) -> MarkDecorator:
        pattern = self.get_suitable_pattern(name)
        not_suitable_error = NotSuitableTagForEvaluationError(f"Tag '{name}' could not be processed!")
        if pattern is None:
            raise not_suitable_error
        match = pattern.match(name)
        if match is None:
            raise not_suitable_error
        reason = match.group("text")
        if reason is None:
            raise NoReasonForMarkDecoratorError(
                f"Tag '{name}' has been used without reason! Please, setup reason using round brackets `(`, `)`\n"
                "For example: `@disabled(TODO: https://tracker.mydomain.com/browse/PRJ-333)`"
            )
        kwargs = {"reason": reason}
        return self._tag_pattern_to_mark_mapping[pattern](**kwargs)
