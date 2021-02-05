import logging
from pathlib import Path
from typing import cast

import pytest

from overhave.testing.settings import OverhaveTestSettings

logger = logging.getLogger(__name__)


class PytestRunner:
    """ Class for running `PyTest` in test and collect-only modes. """

    def __init__(self, test_settings: OverhaveTestSettings) -> None:
        self._test_settings = test_settings

    def run(self, fixture_file: str, alluredir: str) -> int:
        pytest_cmd = [
            fixture_file,
            f"--alluredir={alluredir}",
        ]
        if isinstance(self._test_settings.default_pytest_addoptions, str):
            pytest_cmd.extend(self._test_settings.default_pytest_addoptions.split(" "))
        if isinstance(self._test_settings.extra_pytest_addoptions, str):
            pytest_cmd.extend(self._test_settings.extra_pytest_addoptions.split(" "))

        if self._test_settings.workers is not None:
            pytest_cmd.extend(["-n", f"{self._test_settings.workers}"])

        logger.debug("Prepared pytest args: %s", pytest_cmd)
        return cast(int, pytest.main(pytest_cmd))

    @staticmethod
    def collect_only(fixture_file: Path) -> None:
        logger.info("Started tests collection process with '%s'...", fixture_file.name)
        pytest_cmd = [fixture_file.as_posix(), "--collect-only", "-qq", "--disable-pytest-warnings"]
        logger.debug("Prepared pytest args: %s", pytest_cmd)
        pytest.main(pytest_cmd)
        logger.info("Finished tests collection process with '%s'.", fixture_file.name)
