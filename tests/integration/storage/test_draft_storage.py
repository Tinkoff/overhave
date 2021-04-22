import pytest
from faker import Faker

from overhave import db
from overhave.entities import DraftModel
from overhave.storage.draft_storage import DraftStorage, UniqueDraftCreationError


@pytest.mark.usefixtures("database")
class TestDraftStorage:
    """ Integration tests for :class:`DraftStorage`. """

    def test_get_none_if_not_existing_id(self, test_draft_storage: DraftStorage, faker: Faker):
        assert test_draft_storage.get_draft(faker.random_int()) is None

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_get_draft(self, test_draft_storage: DraftStorage, test_draft: DraftModel):
        draft_model = test_draft_storage.get_draft(test_draft.id)
        assert draft_model.id == test_draft.id
        assert draft_model.published_by == test_draft.published_by
        assert draft_model.pr_url == test_draft.pr_url
        assert draft_model.feature_id == test_draft.feature_id
        assert draft_model.test_run_id == test_draft.test_run_id

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_save_draft(self, test_draft_storage: DraftStorage, test_draft: DraftModel, faker: Faker):
        with pytest.raises(UniqueDraftCreationError):
            test_draft_storage.save_draft(faker.random_int(), test_draft.published_by)
