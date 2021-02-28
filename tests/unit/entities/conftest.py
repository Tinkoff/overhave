import py
import pytest

from overhave import OverhaveFileSettings
from overhave.entities.archiver import ArchiveManager


@pytest.fixture()
def test_file_settings(tmpdir: py.path.local) -> OverhaveFileSettings:
    return OverhaveFileSettings(features_base_dir=tmpdir, tmp_dir=tmpdir)


@pytest.fixture()
def test_archive_manager(test_file_settings: OverhaveFileSettings) -> ArchiveManager:
    return ArchiveManager(file_settings=test_file_settings)
