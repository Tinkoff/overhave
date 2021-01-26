import abc
import logging
import socket
from typing import cast

import sqlalchemy.orm as so

from overhave import db
from overhave.entities import EmulationRunModel
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.utils import get_current_time

logger = logging.getLogger(__name__)


class EmulationStorageError(Exception):
    """ Base Exception for :class:`EmulationStorage`. """


class NotFoundEmulationError(EmulationStorageError):
    """ Exception for situation without saved emulation.. """


class AllPortsAreBusyError(EmulationStorageError):
    """ Exception for situation when all ports are busy. """


class IEmulationStorage(abc.ABC):
    """ Abstract class for emulation runs storage. """

    @abc.abstractmethod
    def create_emulation_run(self, emulation_id: int) -> EmulationRunModel:
        pass

    @abc.abstractmethod
    def get_requested_emulation_run(self, emulation_run_id: int) -> EmulationRunModel:
        pass

    @abc.abstractmethod
    def set_emulation_run_status(self, emulation_run_id: int, status: db.EmulationStatus) -> None:
        pass

    @abc.abstractmethod
    def set_error_emulation_run(self, emulation_run_id: int, traceback: str) -> None:
        pass


class EmulationStorage(IEmulationStorage):
    """ Class for emulation runs storage. """

    def __init__(self, settings: OverhaveEmulationSettings):
        self._settings = settings

    def create_emulation_run(self, emulation_id: int) -> EmulationRunModel:
        with db.create_session() as session:
            emulation_run = db.EmulationRun(emulation_id=emulation_id)
            session.add(emulation_run)
            session.flush()
            return cast(EmulationRunModel, EmulationRunModel.from_orm(emulation_run))

    @staticmethod
    def _get_emulation_run(session: so.Session, emulation_run_id: int) -> db.EmulationRun:
        emulation_run: db.EmulationRun = session.query(db.EmulationRun).get(emulation_run_id)
        if emulation_run is not None:
            return emulation_run
        raise NotFoundEmulationError(f"Not found emulation run with ID {emulation_run_id}!")

    def _get_next_port(self, session: so.Session) -> int:
        allocated_sorted_runs = sorted(
            session.query(db.EmulationRun)
            .filter(db.EmulationRun.port.isnot(None))
            .order_by(db.EmulationRun.id.desc())
            .limit(len(self._settings.emulation_ports))
            .all(),
            key=lambda t: t.changed_at,
        )

        allocated_ports = {run.port for run in allocated_sorted_runs}
        logger.debug("Allocated ports: %s", allocated_ports)
        not_allocated_ports = set(self._settings.emulation_ports).difference(allocated_ports)
        logger.debug("Not allocated ports: %s", not_allocated_ports)
        if not_allocated_ports:
            for port in not_allocated_ports:
                if self._is_port_in_use(port):
                    continue
                return port
            logger.debug("All not allocated ports are busy!")
        for run in allocated_sorted_runs:
            if self._is_port_in_use(run.port):
                continue
            return cast(int, run.port)
        raise AllPortsAreBusyError("All ports are busy - could not find free port!")

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self._settings.emulation_bind_ip, port)) == 0

    def get_requested_emulation_run(self, emulation_run_id: int) -> EmulationRunModel:
        with db.create_session() as session:
            emulation_run = self._get_emulation_run(session, emulation_run_id)
            emulation_run.status = db.EmulationStatus.REQUESTED
            emulation_run.port = self._get_next_port(session)
            emulation_run.changed_at = get_current_time()
            return cast(EmulationRunModel, EmulationRunModel.from_orm(emulation_run))

    def set_emulation_run_status(self, emulation_run_id: int, status: db.EmulationStatus) -> None:
        with db.create_session() as session:
            emulation_run = self._get_emulation_run(session, emulation_run_id)
            if emulation_run.status != status:
                emulation_run.status = status
                emulation_run.changed_at = get_current_time()

    def set_error_emulation_run(self, emulation_run_id: int, traceback: str) -> None:
        with db.create_session() as session:
            emulation_run = self._get_emulation_run(session, emulation_run_id)
            emulation_run.status = db.EmulationStatus.ERROR
            emulation_run.traceback = traceback
            emulation_run.changed_at = get_current_time()
