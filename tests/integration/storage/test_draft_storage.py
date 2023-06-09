import datetime

import allure
import pytest
from faker import Faker

from overhave import db
from overhave.storage import DraftModel, DraftStorage, FeatureModel, SystemUserModel
from overhave.storage.draft_storage import NullableDraftsError, NullableScenarioError
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
class TestDraftStorage:
    """Integration tests for :class:`DraftStorage`."""

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
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

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
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

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
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

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
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

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_save_response(self, test_draft_storage: DraftStorage, test_draft: DraftModel, faker: Faker) -> None:
        pr_url: str = faker.word()
        published_at: datetime.datetime = datetime.datetime.now()
        traceback = faker.word()
        with count_queries(3):
            test_draft_storage.save_response(
                draft_id=test_draft.id,
                pr_url=pr_url,
                published_at=published_at,
                status=db.DraftStatus.REQUESTED,
                traceback=traceback,
            )
        with create_test_session() as session:
            new_test_draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert new_test_draft.pr_url == pr_url
            assert new_test_draft.status is db.DraftStatus.REQUESTED
            assert new_test_draft.traceback == traceback

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    @pytest.mark.parametrize(
        "draft_status",
        [
            db.DraftStatus.REQUESTED,
            db.DraftStatus.CREATING,
            db.DraftStatus.CREATED,
            db.DraftStatus.INTERNAL_ERROR,
            db.DraftStatus.DUPLICATE,
        ],
    )
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

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_previous_feature_draft_with_error(
        self, test_draft_storage: DraftStorage, test_draft: DraftModel
    ) -> None:
        with count_queries(1):
            with pytest.raises(NullableDraftsError):
                test_draft_storage.get_previous_feature_draft(test_draft.feature_id)

    @pytest.mark.parametrize("test_user_role", list(db.Role), indirect=True)
    @pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
    def test_get_previous_draft(
        self,
        test_draft_storage: DraftStorage,
        test_created_test_run_id: int,
        test_second_created_test_run_id: int,
        test_system_user: SystemUserModel,
        test_feature: FeatureModel,
    ) -> None:
        with create_test_session() as session:
            first_test_run: db.TestRun = (
                session.query(db.TestRun).filter(db.TestRun.id == test_created_test_run_id).one()
            )
            test_draft_storage._create_draft(
                session=session,
                test_run=first_test_run,
                published_by=test_system_user.login,
                status=db.DraftStatus.REQUESTED,
            )
            second_test_run: db.TestRun = (
                session.query(db.TestRun).filter(db.TestRun.id == test_second_created_test_run_id).one()
            )
            test_draft_storage._create_draft(
                session=session,
                test_run=second_test_run,
                published_by=test_system_user.login,
                status=db.DraftStatus.DUPLICATE,
            )
        with count_queries(1):
            draft = test_draft_storage.get_previous_feature_draft(feature_id=test_feature.id)
        assert draft.status == db.DraftStatus.DUPLICATE
        assert draft.feature_id == test_feature.id
        assert draft.test_run_id == test_second_created_test_run_id
