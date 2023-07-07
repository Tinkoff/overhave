from datetime import datetime

import allure
import pytest
import sqlalchemy as sa
from faker import Faker

from overhave import db
from overhave.storage import DraftModel, DraftStorage, FeatureModel, SystemUserModel
from overhave.storage.draft_storage import DraftNotFoundError, NullableScenarioError
from overhave.utils import get_current_time
from tests.db_utils import count_queries, create_test_session


@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
@pytest.mark.usefixtures("database")
class TestDraftStorage:
    """Integration tests for :class:`DraftStorage`."""

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_draft(self, test_draft_storage: DraftStorage, test_draft: DraftModel) -> None:
        with count_queries(1):
            with db.create_session() as session:
                draft_model = test_draft_storage.draft_model_by_id(session=session, draft_id=test_draft.id)
        assert draft_model.id == test_draft.id
        assert draft_model.published_by == test_draft.published_by
        assert draft_model.pr_url == test_draft.pr_url
        assert draft_model.feature_id == test_draft.feature_id
        assert draft_model.test_run_id == test_draft.test_run_id

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize("draft_status", [db.DraftStatus.REQUESTED])
    def test_create_new_draft(
        self,
        test_draft_storage: DraftStorage,
        test_created_test_run_id: int,
        draft_status: db.DraftStatus,
        faker: Faker,
    ) -> None:
        with db.create_session() as session:
            with create_test_session():
                test_run: db.TestRun = session.query(db.TestRun).filter(db.TestRun.id == test_created_test_run_id).one()
            with count_queries(3):
                draft_id = test_draft_storage.get_or_create_draft(
                    session=session, test_run=test_run, published_by=test_run.executed_by, status=draft_status
                )
            with create_test_session():
                saved_draft = session.query(db.Draft).filter(db.Draft.id == draft_id).one()
                assert saved_draft.published_by == test_run.executed_by
                assert saved_draft.feature_id == test_run.scenario.feature_id
                assert saved_draft.text == test_run.scenario.text
                assert saved_draft.test_run_id == test_run.id
                assert saved_draft.status == draft_status

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize("draft_status", [db.DraftStatus.REQUESTED])
    def test_create_new_draft_without_text(
        self,
        test_draft_storage: DraftStorage,
        test_created_test_run_id: int,
        draft_status: db.DraftStatus,
        faker: Faker,
    ) -> None:
        with db.create_session() as session:
            with create_test_session():
                test_run: db.TestRun = session.query(db.TestRun).filter(db.TestRun.id == test_created_test_run_id).one()
                test_run.scenario.text = None
                session.flush()
            with count_queries(1):
                with pytest.raises(NullableScenarioError):
                    test_draft_storage.get_or_create_draft(
                        session=session, test_run=test_run, published_by=test_run.executed_by, status=draft_status
                    )

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_existing_draft(self, test_draft_storage: DraftStorage, test_draft: DraftModel, faker: Faker) -> None:
        with db.create_session() as session:
            with create_test_session():
                test_run: db.TestRun = session.query(db.TestRun).filter(db.TestRun.id == test_draft.test_run_id).one()
            with count_queries(1):
                draft_id = test_draft_storage.get_or_create_draft(
                    session=session,
                    test_run=test_run,
                    published_by=test_draft.published_by,
                    status=db.DraftStatus.INTERNAL_ERROR,
                )
            with create_test_session():
                saved_draft = session.query(db.Draft).filter(db.Draft.id == draft_id).one()
                assert saved_draft.id == test_draft.id
                assert saved_draft.published_by == test_draft.published_by
                assert saved_draft.feature_id == test_run.scenario.feature_id
                assert saved_draft.text == test_run.scenario.text
                assert saved_draft.test_run_id == test_draft.test_run_id
                assert saved_draft.status == test_draft.status

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize(("pr_url", "published_at"), [("pr_url", get_current_time())])
    def test_save_response(
        self,
        test_draft_storage: DraftStorage,
        test_feature: FeatureModel,
        test_draft: DraftModel,
        pr_url: str,
        published_at: datetime,
    ) -> None:
        with create_test_session() as session:
            session.execute(
                sa.update(db.Draft).where(db.Draft.id == test_draft.id).values(status=db.DraftStatus.REQUESTED)
            )
        with count_queries(2):
            test_draft_storage.save_response_as_created(
                draft_id=test_draft.id,
                pr_url=pr_url,
                published_at=published_at,
            )
        with create_test_session() as session:
            new_test_draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert new_test_draft.pr_url == pr_url
            assert new_test_draft.status is db.DraftStatus.CREATED
            assert new_test_draft.published_at == published_at
            assert new_test_draft.feature_id == test_feature.id
            assert new_test_draft.feature.released is True

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize("traceback", ["trace", None])
    def test_save_response_as_duplicate_no_draft(
        self, test_draft_storage: DraftStorage, test_feature: FeatureModel, traceback: str | None, faker: Faker
    ) -> None:
        with count_queries(1):
            with pytest.raises(DraftNotFoundError):
                test_draft_storage.save_response_as_duplicate(
                    draft_id=faker.random_int(), feature_id=test_feature.id, traceback=traceback
                )

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize("traceback", ["trace", None])
    @pytest.mark.parametrize(
        ("first_draft_state", "pr_url", "published_at"),
        [(db.DraftStatus.CREATED, "pr_url", get_current_time()), (db.DraftStatus.INTERNAL_ERROR, None, None)],
    )
    def test_save_response_as_duplicate_with_not_succeed_previous_draft(
        self,
        test_draft_storage: DraftStorage,
        service_system_user: SystemUserModel,
        test_feature: FeatureModel,
        test_created_test_run_id: int,
        test_second_created_test_run_id: int,
        traceback: str | None,
        first_draft_state: db.DraftStatus,
        pr_url: str | None,
        published_at: datetime | None,
    ) -> None:
        with create_test_session() as session:
            first_test_run: db.TestRun = (
                session.query(db.TestRun).filter(db.TestRun.id == test_created_test_run_id).one()
            )
            first_draft = db.Draft(
                feature_id=first_test_run.scenario.feature_id,
                test_run_id=first_test_run.id,
                text=first_test_run.scenario.text,
                published_by=service_system_user.login,
                published_at=published_at,
                status=first_draft_state,
                pr_url=pr_url,
            )
            session.add(first_draft)
            session.flush()
            first_draft_id = first_draft.id

            second_test_run: db.TestRun = (
                session.query(db.TestRun).filter(db.TestRun.id == test_second_created_test_run_id).one()
            )
            second_draft = db.Draft(
                feature_id=second_test_run.scenario.feature_id,
                test_run_id=second_test_run.id,
                text=second_test_run.scenario.text,
                published_by=service_system_user.login,
                status=db.DraftStatus.CREATING,
            )
            session.add(second_draft)
            session.flush()
            second_draft_id = second_draft.id

        with count_queries(2):
            test_draft_storage.save_response_as_duplicate(
                draft_id=second_draft_id, feature_id=test_feature.id, traceback=traceback
            )

        with create_test_session() as session:
            first_draft = session.query(db.Draft).filter(db.Draft.id == first_draft_id).one()
            second_draft = session.query(db.Draft).filter(db.Draft.id == second_draft_id).one()
            assert second_draft.status == db.DraftStatus.DUPLICATE
            assert second_draft.feature_id == test_feature.id
            assert second_draft.test_run_id == test_second_created_test_run_id
            assert second_draft.traceback == traceback
            if first_draft_state.is_succeed:
                assert second_draft.published_at == first_draft.published_at
                assert second_draft.pr_url == pr_url
            else:
                assert second_draft.published_at != first_draft.published_at
                assert second_draft.pr_url is None

    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize("draft_status", list(db.DraftStatus))
    @pytest.mark.parametrize("traceback", [None, "random trace str"])
    def test_set_draft_status(
        self,
        test_draft_storage: DraftStorage,
        test_draft: DraftModel,
        draft_status: db.DraftStatus,
        traceback: str | None,
    ) -> None:
        with count_queries(1):
            test_draft_storage.set_draft_status(draft_id=test_draft.id, status=draft_status, traceback=traceback)
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status is draft_status
            assert draft.traceback == traceback
