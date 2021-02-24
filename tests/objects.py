import enum
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, NamedTuple, NewType, Sequence
from unittest import mock

from pydantic import root_validator
from pydantic.main import BaseModel
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from overhave.entities import FeatureExtractor, FeatureTypeName, OverhaveFileSettings

_BLOCKS_DELIMITER = "\n\n"

XDistWorkerValueType = NewType("XDistWorkerValueType", str)
XDistMasterWorker = XDistWorkerValueType("master")


class DataBaseContext(NamedTuple):
    """ Class for easy database entities management through `PyTest` fixtures. """

    metadata: MetaData
    engine: Engine


@lru_cache(maxsize=None)
def get_file_settings() -> OverhaveFileSettings:
    """ Cached OverhaveFileSettings with parameters, corresponding to docs files and examples. """
    test_features_dir = Path(__file__).parent.parent / "docs/includes/features_structure_example"
    return OverhaveFileSettings(
        fixtures_base_dir=test_features_dir, features_base_dir=test_features_dir, tmp_dir=test_features_dir / "tmp"
    )


@lru_cache(maxsize=None)
def get_feature_extractor() -> FeatureExtractor:
    """ Method for getting :class:`FeatureExtractor` with OverhaveFileSettings, based on docs files and examples.

    One of class functions is mocked to prevent the creation of additional files in docs includes.
    """
    with mock.patch.object(FeatureExtractor, "_check_pytest_bdd_scenarios_test_files", return_value=None):
        return FeatureExtractor(file_settings=get_file_settings())


class TestLanguageName(str, enum.Enum):
    """ Enum that declares languages for using in tests. """

    ENG = "en"
    RUS = "ru"


class FeatureTestContainer(BaseModel):
    """ Class for simple test feature operating. """

    type: FeatureTypeName
    name: str
    path: Path
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
def get_test_feature_containers() -> Sequence[FeatureTestContainer]:
    feature_containers: List[FeatureTestContainer] = []
    for value in get_feature_extractor().feature_type_to_dir_mapping.values():
        for item in value.iterdir():
            if item.is_file() and not any((item.name.startswith("."), item.name.startswith("_"))):
                content = item.read_text(encoding="utf-8")
                container = FeatureTestContainer(  # type: ignore
                    type=value.name, name=item.name, path=item, content=content
                )
                feature_containers.append(container)
            continue
    return feature_containers
