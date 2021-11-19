from pathlib import Path

import pytest

from overhave import OverhaveFileSettings
from overhave.entities.archiver import ArchiveManager


@pytest.mark.parametrize("extension", ["zip"])
class TestArchiverManager:
    """Unit tests for :class:`ArchiveManager`."""

    def test_archive_path(
        self,
        extension: str,
        test_archive_manager: ArchiveManager,
        test_file_settings: OverhaveFileSettings,
        test_filepath: Path,
    ) -> None:
        assert test_archive_manager.archive_path(path=test_filepath, extension=extension) == (
            test_file_settings.tmp_reports_dir / test_filepath.name
        ).with_suffix(f".{extension}")

    def test_unpack_path(
        self,
        extension: str,
        test_archive_manager: ArchiveManager,
        test_file_settings: OverhaveFileSettings,
        test_filepath: Path,
    ) -> None:
        archived = test_archive_manager.archive_path(path=test_filepath, extension=extension)
        unpacked = test_archive_manager.unpack_path(path=archived, extension=extension)
        assert unpacked == test_filepath
