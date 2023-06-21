from unittest.mock import MagicMock

import pytest

from overhave import db
from overhave.emulation import Emulator
from overhave.storage import EmulationRunModel
from overhave.transport import EmulationTask
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
class TestEmulator:
    """Tests for emulator class."""

    @pytest.mark.parametrize("emulator_raises_error", [False], indirect=True)
    def test_start_emulation(
        self, emulator: Emulator, emulation_task: EmulationTask, mock_subprocess_popen: MagicMock
    ) -> None:
        with count_queries(8):
            emulator.start_emulation(task=emulation_task)
        with create_test_session() as session:
            emulation_run_db = session.get(db.EmulationRun, emulation_task.data.emulation_run_id)
            emulation_run_model = EmulationRunModel.from_orm(emulation_run_db)
        assert emulation_run_model.status is db.EmulationStatus.READY
        mock_subprocess_popen.assert_called_once()

    @pytest.mark.parametrize("emulator_raises_error", [True], indirect=True)
    def test_start_emulation_with_error(
        self,
        emulator: Emulator,
        emulation_task: EmulationTask,
        mock_subprocess_popen: MagicMock,
    ) -> None:
        with count_queries(8):
            emulator.start_emulation(task=emulation_task)
        with create_test_session() as session:
            emulation_run_db = session.get(db.EmulationRun, emulation_task.data.emulation_run_id)
            emulation_run_model = EmulationRunModel.from_orm(emulation_run_db)
        assert emulation_run_model.status is db.EmulationStatus.ERROR
        mock_subprocess_popen.assert_called_once()
