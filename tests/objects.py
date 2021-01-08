from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, NewType

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from overhave.entities import FeatureExtractor, OverhaveFileSettings


class DataBaseContext(NamedTuple):
    metadata: MetaData
    engine: Engine


XDistWorkerValueType = NewType('XDistWorkerValueType', str)
XDistMasterWorker = XDistWorkerValueType("master")


@lru_cache(maxsize=None)
def get_file_settings() -> OverhaveFileSettings:
    test_features_dir = Path(__file__).parent.parent / 'docs/features_structure_example'
    return OverhaveFileSettings(
        fixtures_base_dir=test_features_dir, features_base_dir=test_features_dir, tmp_dir=test_features_dir / 'tmp'
    )


@lru_cache(maxsize=None)
def get_feature_extractor() -> FeatureExtractor:
    return FeatureExtractor(file_settings=get_file_settings())
