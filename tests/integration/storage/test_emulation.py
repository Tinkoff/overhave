import pytest
import overhave.storage.emulation as emulation
from overhave import db
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.db.statuses import EmulationStatus


class TestEmulation:
    """Integration tests for emulation"""

    def test_raise_exception_for_not_existing_id(self):
        emulation_storage = emulation.EmulationStorage(OverhaveEmulationSettings())
        with pytest.raises(emulation.NotFoundEmulationError):
            emulation_storage.get_requested_emulation_run(-1)

    def test_create_emulation_run(self):
        emulation_run: db.EmulationRun = (emulation.EmulationStorage(OverhaveEmulationSettings())
                                                   .create_emulation_run(1, 'test'))
        assert emulation_run.status == EmulationStatus.CREATED
        assert emulation_run.emulation_id == 1
        assert emulation_run.initiated_by == 'test'
        # Checking port?

    def test_get_requested_emulation_run(self):
        emulation_storage = emulation.EmulationStorage(OverhaveEmulationSettings())
        emulation_storage.create_emulation_run(1, 'test')
        requested_emulation_run: db.EmulationRun = emulation_storage.get_requested_emulation_run(1)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == 1
        # Checking port?

    def test_set_error_run_status(self):
        emulation_storage = emulation.EmulationStorage(OverhaveEmulationSettings())
        emulation_run: db.EmulationRun = emulation_storage.create_emulation_run(1, 'test')
        assert emulation_run.status == EmulationStatus.CREATED
        emulation_storage.set_error_emulation_run(1, 'test set_error_emulation_run')
        assert emulation_run.status == EmulationStatus.ERROR
