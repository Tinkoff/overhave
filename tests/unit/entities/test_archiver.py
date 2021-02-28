from pathlib import Path

import py
from faker import Faker

from overhave.entities.archiver import ArchiveManager


class TestArchiverManager:
    """ Unit tests for :class:`ArchiveManager`. """

    def test_zip_path(self, tmpdir: py.path.local, test_archive_manager: ArchiveManager, faker: Faker):
        path = Path(tmpdir) / faker.word()
        path.mkdir()
        (path / faker.word()).write_text(", ".join(faker.words(faker.random.randint(1, 10))))
        assert test_archive_manager.zip_path(path) == (Path(tmpdir) / "reports" / path.name).with_suffix(".zip")
