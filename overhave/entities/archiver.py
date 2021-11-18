from pathlib import Path
from shutil import make_archive, unpack_archive

from overhave.entities.settings import OverhaveFileSettings


class BaseArchiveManagerException(Exception):
    """Base exception for :class:`ArchiveManager`."""


class IncorrectExtensionError(BaseArchiveManagerException):
    """Exception for situation with specifing incorrect file extension for unpacking."""


class ArchiveManager:
    """Class for files archiving management."""

    def __init__(self, file_settings: OverhaveFileSettings):
        self._file_settings = file_settings

    def archive_path(self, path: Path, extension: str) -> Path:
        zipped = self._file_settings.tmp_reports_dir / path.name
        return Path(make_archive(zipped.as_posix(), extension, path))

    def unpack_path(self, path: Path, extension: str) -> Path:
        if not path.name.endswith(extension):
            raise IncorrectExtensionError(
                "Incorrect file extension '%s' for file '%s' unpacking!", extension, path.name
            )
        extract_path = self._file_settings.tmp_reports_dir / path.name.replace(f".{extension}", "")
        unpack_archive(path.as_posix(), extract_path.as_posix(), extension)
        return extract_path
