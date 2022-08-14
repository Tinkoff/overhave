from pathlib import Path
from typing import Sequence
from unittest import mock

import pytest

from demo.settings import OverhaveDemoAppLanguage
from overhave.scenario import FeatureValidator, StrictFeatureParsingError
from overhave.scenario.validator import FeaturesWithoutIDPresenceError, IncorrectFeaturesPresenceError


def _get_features(test_resolved_validator: FeatureValidator) -> Sequence[Path]:
    return test_resolved_validator._extract_recursively(test_resolved_validator._file_settings.features_dir)


class TestFeatureValidator:
    """Sanity tests for :class:`FeatureValidator`."""

    @pytest.mark.parametrize("test_demo_language", [OverhaveDemoAppLanguage.RU], indirect=True)
    @pytest.mark.parametrize("raise_if_nullable_id", [False])
    def test_validate_not_raise_if_nullable(
        self, test_resolved_validator: FeatureValidator, raise_if_nullable_id: bool
    ) -> None:
        test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)

    @pytest.mark.parametrize("test_demo_language", [OverhaveDemoAppLanguage.RU], indirect=True)
    @pytest.mark.parametrize("raise_if_nullable_id", [True])
    def test_validate_raise_if_nullable(
        self, test_resolved_validator: FeatureValidator, raise_if_nullable_id: bool
    ) -> None:
        with pytest.raises(FeaturesWithoutIDPresenceError):
            test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)
        assert set(test_resolved_validator._nullable_id_features) == set(_get_features(test_resolved_validator))

    @pytest.mark.parametrize("test_demo_language", [OverhaveDemoAppLanguage.RU], indirect=True)
    @pytest.mark.parametrize("raise_if_nullable_id", [False])
    def test_validate_raise_if_incorrect(
        self, test_resolved_validator: FeatureValidator, raise_if_nullable_id: bool
    ) -> None:
        test_resolved_validator._scenario_parser.parse = mock.Mock(  # type: ignore
            side_effect=StrictFeatureParsingError("kek")
        )
        with pytest.raises(IncorrectFeaturesPresenceError):
            test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)
        assert set(test_resolved_validator._incorrect_features) == set(_get_features(test_resolved_validator))
