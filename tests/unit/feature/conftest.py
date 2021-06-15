from functools import lru_cache
from pathlib import Path

from overhave.entities import OverhaveFileSettings


@lru_cache(maxsize=None)
def get_incorrect_test_file_settings() -> OverhaveFileSettings:
    path = Path(__file__).parent
    return OverhaveFileSettings(root_dir=path)
