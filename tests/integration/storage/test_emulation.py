from typing import cast

import pytest
from faker import Faker

import overhave.storage.emulation as e
from overhave import db
from overhave.db.statuses import EmulationStatus
from tests.integration.storage.conftest import commit_emulation_run


class TestEmulationStorage:
    """ Integration tests for :class:`EmulationStorage`. """

    def test_raise_exception_for_not_existing_id(self, test_emulation_storage, faker: Faker):
        with pytest.raises(e.NotFoundEmulationError):
            test_emulation_storage.get_requested_emulation_run(cast(int, faker.random_int()))

    def test_create_emulation_run(self, test_emulation_id, test_emulation_run):
        assert test_emulation_run.status == EmulationStatus.CREATED
        assert test_emulation_run.emulation_id == test_emulation_id
        assert test_emulation_run.initiated_by == db.Role.admin
        assert test_emulation_run.port is None

    def test_get_requested_emulation_run(self, test_emulation_storage, test_emulation_run):
        commit_emulation_run(test_emulation_run)
        requested_emulation_run: db.EmulationRun = test_emulation_storage.get_requested_emulation_run(
            test_emulation_run.id
        )
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == test_emulation_run.emulation_id
        assert test_emulation_storage._is_port_in_use(requested_emulation_run.port)

    def test_set_error_run_status(self, test_emulation_storage, faker: Faker, test_emulation_run):
        commit_emulation_run(test_emulation_run)
        assert test_emulation_run.status == EmulationStatus.CREATED
        test_emulation_storage.set_error_emulation_run(
            emulation_run_id=test_emulation_run.id, traceback=cast(str, faker.sentence())
        )
        assert test_emulation_run.status == EmulationStatus.ERROR
        assert test_emulation_storage._is_port_in_use(test_emulation_run.port)

    @pytest.mark.parametrize(
        "emulation_status",
        [EmulationStatus.READY, EmulationStatus.REQUESTED, EmulationStatus.ERROR, EmulationStatus.CREATED],
    )
    def test_set_emulation_run_status(self, test_emulation_storage, test_emulation_run, emulation_status):
        commit_emulation_run(test_emulation_run)
        test_emulation_storage.set_emulation_run_status(test_emulation_run.id, emulation_status)
        assert test_emulation_run.status == emulation_status
