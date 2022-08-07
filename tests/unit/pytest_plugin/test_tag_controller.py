import pytest
from faker import Faker

from overhave.pytest_plugin.helpers import OverhaveTagController
from overhave.pytest_plugin.helpers.tag_controller import (
    NoReasonForMarkDecoratorError,
    NotSuitableTagForEvaluationError,
    _get_tag_pattern,
)


class TestOverhaveTagController:
    """Unit tests for OverhaveTagController."""

    def test_get_suitable_pattern_no_pattern(self, tag_controller: OverhaveTagController, faker: Faker) -> None:
        assert tag_controller.get_suitable_pattern(faker.word()) is None

    @pytest.mark.parametrize("tag", ["disabled", "xfail"])
    def test_get_suitable_pattern_disabled(self, tag_controller: OverhaveTagController, tag: str) -> None:
        assert tag_controller.get_suitable_pattern(tag) == _get_tag_pattern(tag)

    def test_evaluate_tag_unsuitable(self, tag_controller: OverhaveTagController, faker: Faker) -> None:
        with pytest.raises(NotSuitableTagForEvaluationError):
            tag_controller.evaluate_tag(faker.word())

    @pytest.mark.parametrize("tag", ["disabled", "xfail"])
    def test_evaluate_tag_no_reason(self, tag_controller: OverhaveTagController, tag: str) -> None:
        with pytest.raises(NoReasonForMarkDecoratorError):
            tag_controller.evaluate_tag(tag)

    @pytest.mark.parametrize("tag", ["disabled(kek)"])
    def test_evaluate_tag_disabled(self, tag_controller: OverhaveTagController, tag: str) -> None:
        assert tag_controller.evaluate_tag(tag) == pytest.mark.skip(reason="kek")

    @pytest.mark.parametrize("tag", ["xfail(lol)"])
    def test_evaluate_tag_xfail(self, tag_controller: OverhaveTagController, tag: str) -> None:
        assert tag_controller.evaluate_tag(tag) == pytest.mark.xfail(reason="lol")
