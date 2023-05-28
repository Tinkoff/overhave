from functools import cache
from pathlib import Path
from typing import Dict, List, NewType, Sequence
from unittest import mock

from pydantic import root_validator
from pydantic.main import BaseModel

from demo.settings import OverhaveDemoAppLanguage
from overhave.entities import FeatureExtractor, OverhaveFileSettings
from overhave.storage import FeatureTypeName

_BLOCKS_DELIMITER = "\n\n"

XDistWorkerValueType = NewType("XDistWorkerValueType", str)
XDistMasterWorker = XDistWorkerValueType("master")

PROJECT_WORKDIR = Path(__file__).parent.parent


@cache
def get_test_file_settings() -> OverhaveFileSettings:
    """Cached OverhaveFileSettings with parameters, corresponding to docs files and examples."""
    work_dir = Path(__file__).parent.parent
    root_dir = work_dir / "demo"
    return OverhaveFileSettings(work_dir=work_dir, root_dir=root_dir)


@cache
def get_test_feature_extractor() -> FeatureExtractor:
    """Method for getting :class:`FeatureExtractor` with OverhaveFileSettings, based on docs files and examples.

    One of class functions is mocked to prevent the creation of additional files in docs includes.
    """
    with mock.patch.object(FeatureExtractor, "_check_pytest_bdd_scenarios_test_files", return_value=None):
        return FeatureExtractor(file_settings=get_test_file_settings())


class FeatureTestContainer(BaseModel):
    """Class for simple test feature operating."""

    type: FeatureTypeName
    name: str
    project_path: Path
    content: str
    scenario: str
    language: OverhaveDemoAppLanguage

    @root_validator(pre=True)
    def make_scenario(cls, values: Dict[str, str]) -> Dict[str, str]:
        name = values.get("name")
        content = values.get("content")
        if not isinstance(name, str) or not isinstance(content, str):
            raise ValueError

        blocks = content.split(_BLOCKS_DELIMITER)
        values["scenario"] = _BLOCKS_DELIMITER.join(blocks[1:])

        if OverhaveDemoAppLanguage.RU in name:
            lang = OverhaveDemoAppLanguage.RU
        else:
            lang = OverhaveDemoAppLanguage.EN
        values["language"] = lang
        return values

    @property
    def file_path(self) -> str:
        feature_type_dir = get_test_feature_extractor().feature_type_to_dir_mapping.get(self.type)
        if feature_type_dir is None:
            raise RuntimeError(f"Could not find folder for feature type '{self.type}'!")
        return self.project_path.relative_to(feature_type_dir).as_posix()


@cache
def get_test_feature_containers() -> Sequence[FeatureTestContainer]:
    feature_containers: List[FeatureTestContainer] = []
    for value in get_test_feature_extractor().feature_type_to_dir_mapping.values():
        for item in value.iterdir():
            if not item.is_file() or any((item.name.startswith("."), item.name.startswith("_"))):
                continue
            content = item.read_text(encoding="utf-8")
            container = FeatureTestContainer(  # type: ignore
                type=value.name, name=item.name, project_path=item, content=content
            )
            feature_containers.append(container)
    return feature_containers
