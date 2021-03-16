from typing import cast

import pytest
from faker import Faker

from overhave import db
from overhave.db.statuses import EmulationStatus
from overhave.entities import EmulationRunModel
from overhave.storage.emulation import EmulationStorage, NotFoundEmulationError


class TestEmulationStorage:
    """ Integration tests for :class:`EmulationStorage`. """

    def test_raise_exception_for_not_existing_id(self, test_emulation_storage: EmulationStorage, faker: Faker):
        with pytest.raises(NotFoundEmulationError):
            test_emulation_storage.get_requested_emulation_run(cast(int, faker.random_int()))

    def test_create_emulation_run(self, test_emulation_storage: EmulationStorage, test_emulation: db.Emulation):
        emulation_run = test_emulation_storage.create_emulation_run(test_emulation.id, db.Role.admin)
        assert emulation_run.status == EmulationStatus.CREATED
        assert emulation_run.emulation_id == test_emulation.id
        assert emulation_run.initiated_by == db.Role.admin
        assert emulation_run.port is None

    def test_get_requested_emulation_run(self, test_emulation_storage: EmulationStorage, test_emulation: db.Emulation):
        emulation_run = test_emulation_storage.create_emulation_run(test_emulation.id, db.Role.admin)
        requested_emulation_run: db.EmulationRun = test_emulation_storage.get_requested_emulation_run(emulation_run.id)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == test_emulation.id
        assert not test_emulation_storage._is_port_in_use(requested_emulation_run.port)

    def test_set_error_run_status(
        self, test_emulation_storage: EmulationStorage, faker: Faker, test_emulation: db.Emulation
    ):
        emulation_run = test_emulation_storage.create_emulation_run(test_emulation.id, db.Role.admin)
        assert emulation_run.status == EmulationStatus.CREATED
        test_emulation_storage.set_error_emulation_run(
            emulation_run_id=emulation_run.id, traceback=cast(str, faker.sentence())
        )
        with db.create_session() as session:
            updated_emulation_run = cast(
                EmulationRunModel,
                EmulationRunModel.from_orm(test_emulation_storage._get_emulation_run(session, emulation_run.id)),
            )
        assert updated_emulation_run.status == EmulationStatus.ERROR
        assert not test_emulation_storage._is_port_in_use(updated_emulation_run.port)

    @pytest.mark.parametrize(
        "emulation_status",
        [EmulationStatus.READY, EmulationStatus.REQUESTED, EmulationStatus.ERROR, EmulationStatus.CREATED],
    )
    def test_set_emulation_run_status(
        self, test_emulation_storage: EmulationStorage, test_emulation: db.Emulation, emulation_status: EmulationStatus
    ):
        emulation_run = test_emulation_storage.create_emulation_run(test_emulation.id, db.Role.admin)
        test_emulation_storage.set_emulation_run_status(emulation_run.id, emulation_status)
        with db.create_session() as session:
            updated_emulation_run = cast(
                EmulationRunModel,
                EmulationRunModel.from_orm(test_emulation_storage._get_emulation_run(session, emulation_run.id)),
            )
        assert updated_emulation_run.status == emulation_status
