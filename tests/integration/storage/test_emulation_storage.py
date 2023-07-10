from typing import cast

import pytest
from faker import Faker

from overhave import db
from overhave.db import EmulationStatus
from overhave.storage import EmulationModel, EmulationRunModel, EmulationStorage, SystemUserModel
from tests.db_utils import count_queries, create_test_session


@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
@pytest.mark.usefixtures("database", "socket_mock")
class TestEmulationStorage:
    """Integration tests for :class:`EmulationStorage`."""

    def test_create_emulation_run(
        self,
        test_emulation_storage: EmulationStorage,
        service_system_user: SystemUserModel,
        test_emulation: EmulationModel,
    ) -> None:
        with count_queries(1):
            emulation_run_id = test_emulation_storage.create_emulation_run(
                emulation_id=test_emulation.id, initiated_by=service_system_user.login
            )
        with create_test_session() as session:
            emulation_run = session.query(db.EmulationRun).filter(db.EmulationRun.id == emulation_run_id).one()
            assert emulation_run.status == EmulationStatus.CREATED
            assert emulation_run.emulation_id == test_emulation.id
            assert emulation_run.initiated_by == service_system_user.login
            assert emulation_run.port is None

    def test_get_requested_emulation_run(
        self,
        test_emulation_storage: EmulationStorage,
        test_emulation_run: EmulationRunModel,
    ) -> None:
        with count_queries(7):
            requested_emulation_run = test_emulation_storage.get_requested_emulation_run(test_emulation_run.id)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == test_emulation_run.emulation_id
        assert isinstance(requested_emulation_run.port, int)
        assert not test_emulation_storage._is_port_in_use(requested_emulation_run.port)

    def test_set_error_run_status(
        self,
        test_emulation_storage: EmulationStorage,
        test_emulation_run: EmulationRunModel,
        faker: Faker,
    ) -> None:
        assert test_emulation_run.status is EmulationStatus.CREATED
        with count_queries(1):
            test_emulation_storage.set_error_emulation_run(
                emulation_run_id=test_emulation_run.id, traceback=cast(str, faker.sentence())
            )
        with create_test_session() as session:
            emulation_run = session.query(db.EmulationRun).filter(db.EmulationRun.id == test_emulation_run.id).one()
            assert emulation_run.status == EmulationStatus.ERROR

    @pytest.mark.parametrize(
        "emulation_status",
        [EmulationStatus.READY, EmulationStatus.REQUESTED, EmulationStatus.ERROR, EmulationStatus.CREATED],
    )
    def test_set_emulation_run_status(
        self,
        test_emulation_storage: EmulationStorage,
        test_emulation_run: EmulationRunModel,
        emulation_status: EmulationStatus,
    ) -> None:
        with count_queries(1):
            test_emulation_storage.set_emulation_run_status(test_emulation_run.id, emulation_status)
        with create_test_session() as session:
            emulation_run = session.query(db.EmulationRun).filter(db.EmulationRun.id == test_emulation_run.id).one()
            assert emulation_run.status == emulation_status

    def test_get_emulation_run_by_test_user_id_empty(
        self,
        test_emulation_storage: EmulationStorage,
        service_system_user: SystemUserModel,
        faker: Faker,
    ) -> None:
        fake_id = faker.random_int()
        if fake_id == service_system_user.id:
            fake_id = faker.random_int()
        with count_queries(1):
            filtered_runs = test_emulation_storage.get_emulation_runs_by_test_user_id(test_user_id=fake_id)
        assert not filtered_runs

    def test_get_emulation_run_by_test_user_id(
        self,
        test_emulation_storage: EmulationStorage,
        service_system_user: SystemUserModel,
        test_emulation_run: EmulationRunModel,
        faker: Faker,
    ) -> None:
        with count_queries(4):
            filtered_runs = test_emulation_storage.get_emulation_runs_by_test_user_id(
                test_user_id=service_system_user.id
            )
        assert len(filtered_runs) == 1
        assert filtered_runs[0] == test_emulation_run
