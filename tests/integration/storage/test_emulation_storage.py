from typing import cast

import pytest
from faker import Faker

from overhave import db
from overhave.db import EmulationStatus
from overhave.storage import EmulationRunModel, EmulationStorage, SystemUserModel
from overhave.storage.emulation_storage import NotFoundEmulationError
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database", "socket_mock")
class TestEmulationStorage:
    """Integration tests for :class:`EmulationStorage`."""

    def test_raise_exception_for_not_existing_id(self, test_emulation_storage: EmulationStorage, faker: Faker) -> None:
        with count_queries(1):
            with pytest.raises(NotFoundEmulationError):
                test_emulation_storage.get_requested_emulation_run(cast(int, faker.random_int()))

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_create_emulation_run(
        self, test_emulation_storage: EmulationStorage, test_system_user: SystemUserModel, test_emulation: db.Emulation
    ) -> None:
        with count_queries(4):
            emulation_run = test_emulation_storage.create_emulation_run(
                emulation_id=test_emulation.id, initiated_by=test_system_user.login
            )
        assert emulation_run.status == EmulationStatus.CREATED
        assert emulation_run.emulation_id == test_emulation.id
        assert emulation_run.initiated_by == test_system_user.login
        assert emulation_run.port is None

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_requested_emulation_run(
        self, test_emulation_storage: EmulationStorage, test_system_user: SystemUserModel, test_emulation: db.Emulation
    ) -> None:
        with count_queries(4):
            emulation_run = test_emulation_storage.create_emulation_run(
                emulation_id=test_emulation.id, initiated_by=test_system_user.login
            )
        with count_queries(7):
            requested_emulation_run = test_emulation_storage.get_requested_emulation_run(emulation_run.id)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == test_emulation.id
        assert isinstance(requested_emulation_run.port, int)
        assert not test_emulation_storage._is_port_in_use(requested_emulation_run.port)

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_set_error_run_status(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        faker: Faker,
    ) -> None:
        with count_queries(4):
            emulation_run = test_emulation_storage.create_emulation_run(
                emulation_id=test_emulation.id, initiated_by=test_system_user.login
            )
        assert emulation_run.status == EmulationStatus.CREATED
        with count_queries(2):
            test_emulation_storage.set_error_emulation_run(
                emulation_run_id=emulation_run.id, traceback=cast(str, faker.sentence())
            )
        with create_test_session() as session:
            emulation_run = EmulationRunModel.from_orm(
                test_emulation_storage._get_emulation_run(session, emulation_run.id)
            )
        assert emulation_run.status == EmulationStatus.ERROR
        assert emulation_run.port is None

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    @pytest.mark.parametrize(
        "emulation_status",
        [EmulationStatus.READY, EmulationStatus.REQUESTED, EmulationStatus.ERROR, EmulationStatus.CREATED],
    )
    def test_set_emulation_run_status(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        emulation_status: EmulationStatus,
    ) -> None:
        with count_queries(4):
            emulation_run = test_emulation_storage.create_emulation_run(
                emulation_id=test_emulation.id, initiated_by=test_system_user.login
            )
        with count_queries(1):
            test_emulation_storage.set_emulation_run_status(emulation_run.id, emulation_status)
        with create_test_session() as session:
            emulation_run = EmulationRunModel.from_orm(
                test_emulation_storage._get_emulation_run(session, emulation_run.id)
            )
        assert emulation_run.status == emulation_status

    def test_get_emulation_run_by_test_user_id_empty(
        self,
        test_emulation_storage: EmulationStorage,
        faker: Faker,
    ) -> None:
        with count_queries(1):
            filtered_runs = test_emulation_storage.get_emulation_runs_by_test_user_id(test_user_id=faker.random_int())
        assert not filtered_runs

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_emulation_run_by_test_user_id(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        faker: Faker,
    ) -> None:
        with count_queries(4):
            emulation_run = test_emulation_storage.create_emulation_run(
                emulation_id=test_emulation.id, initiated_by=test_system_user.login
            )
        with count_queries(4):
            filtered_runs = test_emulation_storage.get_emulation_runs_by_test_user_id(test_user_id=test_system_user.id)
        assert len(filtered_runs) == 1
        assert filtered_runs[0] == emulation_run
