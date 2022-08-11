from unittest import mock

import allure_commons.types
import pytest
from faker import Faker

from overhave.pytest_plugin.helpers import OverhaveTagController
from overhave.pytest_plugin.helpers.tag_controller import NoReasonForMarkDecoratorError, TagEvaluationResult


class TestOverhaveTagController:
    """Unit tests for OverhaveTagController."""

    def test_get_suitable_pattern_no_pattern(self, tag_controller: OverhaveTagController, faker: Faker) -> None:
        assert tag_controller.get_suitable_parsing_model(faker.word()) is None

    @pytest.mark.parametrize("tag", ["disabled", "xfail", "disabled(kek)", "xfail(lol)"])
    def test_get_suitable_pattern(self, tag_controller: OverhaveTagController, tag: str) -> None:
        clear_tag = tag.split("(")[0]
        assert tag_controller.get_suitable_parsing_model(tag) == tag_controller._tag_to_parsing_model_mapping[clear_tag]

    @pytest.mark.parametrize("tag", ["disabled_smth", "xfail_smth", "smth_disabled", "smth_xfail"])
    def test_get_suitable_pattern_not_matched(self, tag_controller: OverhaveTagController, tag: str) -> None:
        assert tag_controller.get_suitable_parsing_model(tag) is None

    @pytest.mark.parametrize("tag", ["disabled", "xfail"])
    def test_evaluate_tag_no_reason(self, tag_controller: OverhaveTagController, tag: str) -> None:
        with pytest.raises(NoReasonForMarkDecoratorError):
            tag_controller.evaluate_tag(name=tag, parsing_model=mock.MagicMock())

    @pytest.mark.parametrize(
        ("tag", "result"),
        [
            (
                "disabled(kek)",
                TagEvaluationResult(
                    marker=pytest.mark.skip(reason="kek"), url=None, link_type=allure_commons.types.LinkType.LINK
                ),
            ),
            (
                "disabled(TODO: https://link/to/disabling/reason; deadline: 01.01.99)",
                TagEvaluationResult(
                    marker=pytest.mark.skip(reason="TODO: https://link/to/disabling/reason; deadline: 01.01.99"),
                    url="https://link/to/disabling/reason",
                    link_type=allure_commons.types.LinkType.LINK,
                ),
            ),
            (
                "xfail(lol)",
                TagEvaluationResult(
                    marker=pytest.mark.xfail(reason="lol"), url=None, link_type=allure_commons.types.LinkType.ISSUE
                ),
            ),
            (
                "xfail(wait until bug https://link/to/bug will be fixed)",
                TagEvaluationResult(
                    marker=pytest.mark.xfail(reason="wait until bug https://link/to/bug will be fixed"),
                    url="https://link/to/bug",
                    link_type=allure_commons.types.LinkType.ISSUE,
                ),
            ),
        ],
    )
    def test_evaluate_tag(self, tag_controller: OverhaveTagController, tag: str, result: TagEvaluationResult) -> None:
        parsing_model = tag_controller.get_suitable_parsing_model(tag)
        assert parsing_model is not None
        assert tag_controller.evaluate_tag(name=tag, parsing_model=parsing_model) == result
