import logging
from pathlib import Path
from typing import List, Optional

import pytest

from overhave.test_execution.settings import OverhaveTestSettings

logger = logging.getLogger(__name__)


class PytestRunner:
    """ Class for running `PyTest` in test and collect-only modes. """

    def __init__(self, settings: OverhaveTestSettings) -> None:
        self._settings = settings

    @staticmethod
    def _extend_cmd_args(cmd: List[str], addoptions: Optional[str]) -> None:
        if not isinstance(addoptions, str):
            return
        cmd.extend(addoptions.split(" "))

    def run(self, fixture_file: str, alluredir: str) -> int:
        pytest_cmd = [fixture_file, f"--alluredir={alluredir}"]
        for addoptions in (self._settings.default_pytest_addoptions, self._settings.extra_pytest_addoptions):
            self._extend_cmd_args(cmd=pytest_cmd, addoptions=addoptions)
        if self._settings.workers is not None:
            pytest_cmd.extend(["-n", f"{self._settings.workers}"])

        logger.debug("Prepared pytest args: %s", pytest_cmd)
        return pytest.main(pytest_cmd)

    def collect_only(self, fixture_file: Path) -> None:
        logger.info("Started tests collection process with '%s'...", fixture_file.name)
        pytest_cmd = [
            fixture_file.as_posix(),
            "--collect-only",
            "-qq",
            "--disable-pytest-warnings",
        ]
        self._extend_cmd_args(cmd=pytest_cmd, addoptions=self._settings.extra_pytest_addoptions)
        logger.debug("Prepared pytest args: %s", pytest_cmd)
        pytest.main(pytest_cmd)
        logger.info("Finished tests collection process with '%s'.", fixture_file.name)
