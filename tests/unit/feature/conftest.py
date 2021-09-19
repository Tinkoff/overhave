from functools import cache
from pathlib import Path

from overhave.entities import OverhaveFileSettings


@cache
def get_incorrect_test_file_settings() -> OverhaveFileSettings:
    path = Path(__file__).parent
    return OverhaveFileSettings(root_dir=path)
