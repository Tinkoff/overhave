from functools import lru_cache
from pathlib import Path
from typing import Sequence, cast

import pytest
from _pytest.fixtures import FixtureRequest

from overhave.entities import FeatureExtractor, OverhaveFileSettings
from tests.objects import FeatureTestContainer, get_test_feature_containers


@lru_cache(maxsize=None)
def get_incorrect_test_file_settings() -> OverhaveFileSettings:
    path = Path(__file__).parent
    return OverhaveFileSettings(features_base_dir=path, fixtures_base_dir=path, tmp_dir=path)


@pytest.fixture()
def test_feature_extractor(request: FixtureRequest) -> FeatureExtractor:
    if hasattr(request, "param"):
        return cast(FeatureExtractor, request.param)
    raise NotImplementedError


@pytest.fixture(scope="class")
def test_feature_containers() -> Sequence[FeatureTestContainer]:
    return get_test_feature_containers()
