from functools import lru_cache
from pathlib import Path
from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest

from overhave.entities import FeatureExtractor, OverhaveFileSettings


@lru_cache(maxsize=None)
def get_incorrect_test_file_settings() -> OverhaveFileSettings:
    path = Path(__file__).parent
    return OverhaveFileSettings(root_dir=path)


@pytest.fixture()
def test_feature_extractor(request: FixtureRequest) -> FeatureExtractor:
    if hasattr(request, "param"):
        return cast(FeatureExtractor, request.param)
    raise NotImplementedError
