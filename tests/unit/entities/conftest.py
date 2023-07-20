from pathlib import Path
from uuid import uuid1

import py
import pytest
from faker import Faker

from overhave import OverhaveFileSettings
from overhave.entities.archiver import ArchiveManager


@pytest.fixture()
def test_file_settings(tmpdir: py.path.local) -> OverhaveFileSettings:
    settings = OverhaveFileSettings(work_dir=Path(tmpdir), root_dir=Path(tmpdir), tmp_dir=Path(tmpdir / "tmp"))
    settings.tmp_reports_dir.mkdir(parents=True)
    return settings


@pytest.fixture()
def test_archive_manager(test_file_settings: OverhaveFileSettings) -> ArchiveManager:
    return ArchiveManager(file_settings=test_file_settings)


@pytest.fixture()
def test_filepath(test_file_settings: OverhaveFileSettings, faker: Faker) -> Path:
    path = test_file_settings.tmp_reports_dir / uuid1().hex
    path.mkdir()
    (path / faker.word()).write_text(", ".join(faker.words(faker.random.randint(1, 10))))
    return path
