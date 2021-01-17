import enum
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, NamedTuple, NewType, Sequence

from pydantic import root_validator
from pydantic.main import BaseModel
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from overhave.entities import FeatureExtractor, OverhaveFileSettings

_BLOCKS_DELIMITER = "\n\n"

XDistWorkerValueType = NewType('XDistWorkerValueType', str)
XDistMasterWorker = XDistWorkerValueType("master")


class DataBaseContext(NamedTuple):
    """ Class for easy database entities management through `PyTest` fixtures. """

    metadata: MetaData
    engine: Engine


@lru_cache(maxsize=None)
def get_file_settings() -> OverhaveFileSettings:
    test_features_dir = Path(__file__).parent.parent / 'docs/includes/features_structure_example'
    return OverhaveFileSettings(
        fixtures_base_dir=test_features_dir, features_base_dir=test_features_dir, tmp_dir=test_features_dir / 'tmp'
    )


@lru_cache(maxsize=None)
def get_feature_extractor() -> FeatureExtractor:
    return FeatureExtractor(file_settings=get_file_settings())


class TestLanguageName(str, enum.Enum):
    """ Enum that declares languages for using in tests. """

    ENG = "en"
    RUS = "ru"


class TestFeatureContainer(BaseModel):
    """ Class for simple test feature operating. """

    name: str
    content: str
    scenario: str
    language: TestLanguageName

    @root_validator(pre=True)
    def make_scenario(cls, values: Dict[str, str]) -> Dict[str, str]:
        name = values.get("name")
        content = values.get("content")
        if not isinstance(name, str) or not isinstance(content, str):
            raise ValueError

        blocks = content.split(_BLOCKS_DELIMITER)
        values["scenario"] = _BLOCKS_DELIMITER.join(blocks[1:])

        if TestLanguageName.RUS in name:
            lang = TestLanguageName.RUS
        else:
            lang = TestLanguageName.ENG
        values["language"] = lang
        return values


@lru_cache(maxsize=None)
def get_test_feature_containers() -> Sequence[TestFeatureContainer]:
    feature_containers: List[TestFeatureContainer] = []
    for value in get_feature_extractor().feature_type_to_dir_mapping.values():
        for item in value.iterdir():
            if item.is_file() and not any((item.name.startswith("."), item.name.startswith("_"))):
                content = item.read_text(encoding="utf-8")
                container = TestFeatureContainer(name=item.name, content=content)  # type: ignore
                feature_containers.append(container)
            continue
    return feature_containers
