import pytest
from faker import Faker

import overhave.storage.emulation as e
from overhave import db
from overhave.db.statuses import EmulationStatus
from conftest import ADMIN


class TestEmulationStorage:
    """ Integration tests for :class:`EmulationStorage`. """

    def test_raise_exception_for_not_existing_id(self, test_emulation_storage, test_add_emulation_to_db):
        test_emulation_storage.create_emulation_run(emulation_id=test_add_emulation_to_db, initiated_by=ADMIN)
        with pytest.raises(e.NotFoundEmulationError):
            test_emulation_storage.get_requested_emulation_run(-1)

    def test_create_emulation_run(self, test_emulation_storage, test_add_emulation_to_db):
        emulation_run: db.EmulationRun = test_emulation_storage.create_emulation_run(
            emulation_id=test_add_emulation_to_db, initiated_by=ADMIN
        )
        assert emulation_run.status == EmulationStatus.CREATED
        assert emulation_run.emulation_id == test_add_emulation_to_db
        assert emulation_run.initiated_by == ADMIN
        assert emulation_run.port is None

    def test_get_requested_emulation_run(self, test_emulation_storage, test_add_emulation_to_db):
        test_emulation_storage.create_emulation_run(emulation_id=test_add_emulation_to_db, initiated_by=ADMIN)
        requested_emulation_run: db.EmulationRun = test_emulation_storage.get_requested_emulation_run(1)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == test_add_emulation_to_db
        assert test_emulation_storage._is_port_in_use(requested_emulation_run.port)

    def test_set_error_run_status(self, test_emulation_storage, test_add_emulation_to_db):
        emulation_run: db.EmulationRun = test_emulation_storage.create_emulation_run(
            emulation_id=test_add_emulation_to_db, initiated_by=ADMIN
        )
        assert emulation_run.status == EmulationStatus.CREATED
        test_emulation_storage.set_error_emulation_run(emulation_run_id=emulation_run.id, traceback=Faker().sentence())
        assert emulation_run.status == EmulationStatus.ERROR
        assert test_emulation_storage._is_port_in_use(emulation_run.port)

    def test_set_emulation_run_status(self, test_emulation_storage, test_add_emulation_to_db):
        emulation_run: db.EmulationRun = test_emulation_storage.create_emulation_run(
            emulation_id=test_add_emulation_to_db, initiated_by=ADMIN
        )
        test_emulation_storage.set_emulation_run_status(emulation_run.id, EmulationStatus.READY)
        assert emulation_run.status == EmulationStatus.READY
        test_emulation_storage.set_emulation_run_status(emulation_run.id, EmulationStatus.REQUESTED)
        assert emulation_run.status == EmulationStatus.REQUESTED
        test_emulation_storage.set_emulation_run_status(emulation_run.id, EmulationStatus.ERROR)
        assert emulation_run.status == EmulationStatus.ERROR
        test_emulation_storage.set_emulation_run_status(emulation_run.id, EmulationStatus.CREATED)
        assert emulation_run.status == EmulationStatus.CREATED
