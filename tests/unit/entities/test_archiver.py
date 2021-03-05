from pathlib import Path

import py
import pytest
from faker import Faker

from overhave.entities.archiver import ArchiveManager


@pytest.mark.parametrize("extension", ["zip"])
class TestArchiverManager:
    """ Unit tests for :class:`ArchiveManager`. """

    def test_zip_path(self, extension: str, tmpdir: py.path.local, test_archive_manager: ArchiveManager, faker: Faker):
        path = Path(tmpdir) / faker.word()
        path.mkdir()
        (path / faker.word()).write_text(", ".join(faker.words(faker.random.randint(1, 10))))
        assert test_archive_manager.archive_path(path=path, extension=extension) == (
            Path(tmpdir) / "reports" / path.name
        ).with_suffix(f".{extension}")
