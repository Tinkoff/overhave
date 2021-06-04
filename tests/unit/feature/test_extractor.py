from typing import Sequence

import pytest
from faker import Faker

from overhave.entities import (
    FeatureExtractor,
    FeatureTypeExtractionError,
    OverhaveFileSettings,
    ScenariosTestFileNotFound,
)
from tests.objects import FeatureTestContainer, get_test_feature_extractor
from tests.unit.feature.conftest import get_incorrect_test_file_settings


class TestFeatureExtractor:
    """ Unit tests for :class:`FeatureExtractor`. """

    @pytest.mark.parametrize("test_file_settings", [get_incorrect_test_file_settings()], indirect=True)
    def test_feature_type_extraction_error(self, test_file_settings: OverhaveFileSettings) -> None:
        with pytest.raises(FeatureTypeExtractionError):
            FeatureExtractor(file_settings=test_file_settings)._extract_project_data()

    @pytest.mark.parametrize("test_file_settings", [get_incorrect_test_file_settings()], indirect=True)
    def test_scenarios_test_file_not_found_error(self, test_file_settings: OverhaveFileSettings, faker: Faker) -> None:
        extractor = FeatureExtractor(file_settings=test_file_settings)
        extractor._feature_types = [faker.word()]
        with pytest.raises(ScenariosTestFileNotFound):  # noqa: PT012
            extractor._check_pytest_bdd_scenarios_test_files()

    @pytest.mark.parametrize("test_feature_extractor", [get_test_feature_extractor()], indirect=True)
    def test_feature_extractor_properties(
        self, test_feature_extractor: FeatureExtractor, test_feature_containers: Sequence[FeatureTestContainer]
    ) -> None:
        assert set(test_feature_extractor.feature_types) == {feature.type for feature in test_feature_containers}
        assert test_feature_extractor.feature_type_to_dir_mapping == {
            feature.type: feature.project_path.parent for feature in test_feature_containers
        }
