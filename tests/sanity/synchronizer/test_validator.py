from pathlib import Path
from typing import Sequence
from unittest import mock

import pytest

from demo.settings import OverhaveDemoAppLanguage
from overhave.scenario import FeatureValidator, StrictFeatureParsingError
from overhave.scenario.validator.errors import (
    DuplicateFeatureIDError,
    FeaturesWithoutIDPresenceError,
    IncorrectFeaturesPresenceError,
)


def _get_features(test_resolved_validator: FeatureValidator) -> Sequence[Path]:
    return test_resolved_validator._extract_recursively(test_resolved_validator._file_settings.features_dir)


@pytest.mark.parametrize("test_demo_language", [OverhaveDemoAppLanguage.RU], indirect=True)
class TestFeatureValidator:
    """Sanity tests for :class:`FeatureValidator`."""

    @pytest.mark.parametrize("raise_if_nullable_id", [False])
    def test_validate_not_raise_if_nullable(
        self, test_resolved_validator: FeatureValidator, raise_if_nullable_id: bool
    ) -> None:
        test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)

    @pytest.mark.parametrize("raise_if_nullable_id", [True])
    def test_validate_raise_if_nullable(
        self, test_resolved_validator: FeatureValidator, raise_if_nullable_id: bool
    ) -> None:
        with pytest.raises(FeaturesWithoutIDPresenceError):
            test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)
        assert set(test_resolved_validator._nullable_id_features) == set(_get_features(test_resolved_validator))

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

    @pytest.mark.parametrize("raise_if_nullable_id", [False])
    @pytest.mark.parametrize("duplicate_id_mapping", [{123: [Path("/feature_with_id")]}])
    def test_validate_raise_if_no_duplicate_ids(
        self,
        test_resolved_validator: FeatureValidator,
        raise_if_nullable_id: bool,
        duplicate_id_mapping: dict[int, list[Path]],
    ) -> None:
        test_resolved_validator._feature_id_to_path_mapping = duplicate_id_mapping.copy()
        test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)
        assert test_resolved_validator._feature_id_to_path_mapping == duplicate_id_mapping

    @pytest.mark.parametrize("raise_if_nullable_id", [False])
    @pytest.mark.parametrize(
        "duplicate_id_mapping", [{123: [Path("/feature_with_duplicate_id1"), Path("/feature_with_duplicate_id2")]}]
    )
    def test_validate_raise_if_duplicate_ids(
        self,
        test_resolved_validator: FeatureValidator,
        raise_if_nullable_id: bool,
        duplicate_id_mapping: dict[int, list[Path]],
    ) -> None:
        test_resolved_validator._feature_id_to_path_mapping = duplicate_id_mapping.copy()
        with pytest.raises(DuplicateFeatureIDError):
            test_resolved_validator.validate(raise_if_nullable_id=raise_if_nullable_id)
        assert test_resolved_validator._feature_id_to_path_mapping == duplicate_id_mapping
