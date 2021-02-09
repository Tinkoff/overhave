import json
import logging
import re
import subprocess
from functools import cached_property
from typing import Pattern

from overhave import db
from overhave.entities.converters import EmulationRunModel
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.redis import EmulationTask
from overhave.storage import EmulationStorageError, IEmulationStorage

logger = logging.getLogger(__name__)


class EmulationError(Exception):
    """ Base exception for :class:`Emulator`. """


class DangerousExternalCommandError(EmulationError):
    """ Exception for dangerous command error. """


class EmulationNotEnabledError(EmulationError):
    """ Exception for not enabled emulation (```emulation_base_cmd``` not specified). """


_EMULATION_NOT_ENABLED_MSG = "Emulation not enabled: 'emulation_base_cmd' has not been specified!"


class ExternalCommandCheckMixin:
    """ Mixin for simple command-line command checking. """

    @cached_property
    def _dangerous_pattern(self) -> Pattern[str]:
        return re.compile(r"[$|><]+")

    def _check_dangerous(self, cmd: str) -> None:
        if self._dangerous_pattern.match(cmd) is not None:
            raise DangerousExternalCommandError(f"Dangerous external command: '{cmd}'")


class Emulator(ExternalCommandCheckMixin):
    """ Class for creation of emulation runs. """

    def __init__(self, storage: IEmulationStorage, settings: OverhaveEmulationSettings):
        self._storage = storage
        self._settings = settings
        if not self._settings.enabled:
            raise EmulationNotEnabledError(_EMULATION_NOT_ENABLED_MSG)

    def _initiate(self, emulation_run: EmulationRunModel) -> None:
        cmd_from_user = emulation_run.emulation.command.strip()
        self._check_dangerous(cmd_from_user)

        if not isinstance(self._settings.emulation_base_cmd, str):
            raise EmulationNotEnabledError(_EMULATION_NOT_ENABLED_MSG)

        emulation_base_cmd = self._settings.emulation_base_cmd.format(
            feature_type=emulation_run.emulation.test_user.feature_type.name
        ).split(" ")

        emulation_cmd = (
            [self._settings.emulation_core_path]
            + self._settings.emulation_prefix.format(
                address=self._settings.emulation_bind_ip,
                port=emulation_run.port,
                timeout=self._settings.wait_timeout_seconds,
            ).split(" ")
            + emulation_base_cmd
            + cmd_from_user.split(" ")
        )
        if isinstance(self._settings.emulation_postfix, str):
            emulation_cmd += self._settings.emulation_postfix.format(
                name=emulation_run.emulation.test_user.name.replace(" ", "_"),
                model=json.dumps(emulation_run.emulation.test_user.specification).replace(' ', ''),
            ).split(" ")
        logger.debug("Emulation command: %s", " ".join(emulation_cmd))
        try:
            subprocess.Popen(emulation_cmd)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error("Error while starting emulation process!")
            raise EmulationError(e)

    def start_emulation(self, task: EmulationTask) -> None:
        emulation_run_id = task.data.emulation_run_id
        try:
            emulation_run = self._storage.get_requested_emulation_run(emulation_run_id)
            logger.info("Try to emulate: %s", emulation_run.emulation)
            self._initiate(emulation_run)
            self._storage.set_emulation_run_status(emulation_run_id=emulation_run.id, status=db.EmulationStatus.READY)
        except (EmulationError, EmulationStorageError) as e:
            logger.exception("Could not emulate task %s!", task)
            self._storage.set_error_emulation_run(emulation_run_id=emulation_run_id, traceback=str(e))
