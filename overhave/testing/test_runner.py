import logging
from pathlib import Path
from typing import List, Optional, cast

import pytest

from overhave.entities import OverhaveFileSettings
from overhave.testing.settings import OverhaveTestSettings

logger = logging.getLogger(__name__)


class PytestRunner:
    """ Class for running `PyTest` in test and collect-only modes. """

    def __init__(self, test_settings: OverhaveTestSettings, file_settings: OverhaveFileSettings) -> None:
        self._test_settings = test_settings
        self._file_settings = file_settings

    @staticmethod
    def _extend_cmd_args(cmd: List[str], addoptions: Optional[str]) -> None:
        if not isinstance(addoptions, str):
            return
        cmd.extend(addoptions.split(" "))

    def run(self, fixture_file: str, alluredir: str) -> int:
        pytest_cmd = [fixture_file, f"--alluredir={alluredir}", f"--rootdir={self._file_settings.root_dir}"]
        for addoptions in (self._test_settings.default_pytest_addoptions, self._test_settings.extra_pytest_addoptions):
            self._extend_cmd_args(cmd=pytest_cmd, addoptions=addoptions)
        if self._test_settings.workers is not None:
            pytest_cmd.extend(["-n", f"{self._test_settings.workers}"])

        logger.debug("Prepared pytest args: %s", pytest_cmd)
        return cast(int, pytest.main(pytest_cmd))

    def collect_only(self, fixture_file: Path) -> None:
        logger.info("Started tests collection process with '%s'...", fixture_file.name)
        pytest_cmd = [
            fixture_file.as_posix(),
            f"--rootdir={self._file_settings.root_dir}",
            "--collect-only",
            "-qq",
            "--disable-pytest-warnings",
        ]
        self._extend_cmd_args(cmd=pytest_cmd, addoptions=self._test_settings.extra_pytest_addoptions)
        logger.debug("Prepared pytest args: %s", pytest_cmd)
        pytest.main(pytest_cmd)
        logger.info("Finished tests collection process with '%s'.", fixture_file.name)
