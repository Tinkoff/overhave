from pathlib import Path
from shutil import make_archive

from overhave.entities.settings import OverhaveFileSettings


class ArchiveManager:
    """ Class for files archiving management. """

    def __init__(self, file_settings: OverhaveFileSettings):
        self._file_settings = file_settings

    def zip_path(self, path: Path) -> Path:
        zipped = self._file_settings.tmp_reports_dir / path.name
        return Path(make_archive(zipped.as_posix(), "zip", path))
