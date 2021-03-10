import pytest

import overhave.storage.emulation as e
from overhave import db
from overhave.db.statuses import EmulationStatus
from overhave.entities.settings import OverhaveEmulationSettings


class TestEmulation:
    """Integration tests for emulation"""

    @pytest.fixture()
    def test_emulation_settings(self) -> OverhaveEmulationSettings:
        return OverhaveEmulationSettings()

    @pytest.fixture()
    def test_emulation_storage(self, test_emulation_settings) -> e.EmulationStorage:
        return e.EmulationStorage(test_emulation_settings)

    @pytest.fixture
    def test_add_emulation_to_db(self):
        # TRASH????????
        emulation: db.tables.Emulation = db.tables.Emulation()
        emulation.id = 1
        emulation.name = 'test'
        emulation.command = 'test'
        emulation.created_by = 'admin'
        emulation.test_user_id = 0
        test_user = db.tables.TestUser()
        test_user.id = 0
        test_user.created_by = 'admin'
        test_user.feature_type_id = 0
        test_user.name = 'test'
        feature_type = db.tables.FeatureType()
        feature_type.name = 'test'
        feature_type.id = -10
        with db.create_session() as session:
            session.add(feature_type)
            session.add(test_user)
            session.add(emulation)
            session.flush()

    def test_raise_exception_for_not_existing_id(self, test_emulation_storage, test_add_emulation_to_db):
        test_emulation_storage.create_emulation_run(1, "admin")
        with pytest.raises(e.NotFoundEmulationError):
            test_emulation_storage.get_requested_emulation_run(-1)

    def test_create_emulation_run(self, test_emulation_storage, test_add_emulation_to_db):
        emulation_run: db.EmulationRun = test_emulation_storage.create_emulation_run(1, "admin")
        assert emulation_run.status == EmulationStatus.CREATED
        assert emulation_run.emulation_id == 1
        assert emulation_run.initiated_by == "admin"
        # Checking port?

    def test_get_requested_emulation_run(self, test_emulation_storage, test_add_emulation_to_db):
        test_emulation_storage.create_emulation_run(1, "admin")
        requested_emulation_run: db.EmulationRun = test_emulation_storage.get_requested_emulation_run(1)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == 1
        # Checking port?

    def test_set_error_run_status(self, test_emulation_storage, test_add_emulation_to_db):
        emulation_run: db.EmulationRun = test_emulation_storage.create_emulation_run(1, "admin")
        assert emulation_run.status == EmulationStatus.CREATED
        test_emulation_storage.set_error_emulation_run(1, "test set_error_emulation_run")
        assert emulation_run.status == EmulationStatus.ERROR
