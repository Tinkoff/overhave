from pathlib import Path
from typing import List


class BaseFileExtractor:
    """Base class for file extraction."""

    def __init__(self, extenstion: str) -> None:
        self._extenstion = extenstion

    @staticmethod
    def _check_dir_compliance(path: Path) -> bool:
        return all((path.is_dir(), not path.name.startswith("."), not path.name.startswith("_")))

    def _check_file_compliance(self, path: Path) -> bool:
        return all(
            (
                not path.is_dir(),
                path.suffix == self._extenstion,
                not path.name.startswith("."),
                not path.name.startswith("_"),
            )
        )

    def _extract_recursively(self, folder: Path) -> List[Path]:
        files = []
        for path in folder.iterdir():
            if self._check_dir_compliance(path):
                subdirs = self._extract_recursively(path)
                files.extend(subdirs)
                continue
            if not self._check_file_compliance(path):
                continue
            files.append(path)
        return files
