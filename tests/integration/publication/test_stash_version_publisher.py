from datetime import datetime

import allure
import httpx
import pytest

from overhave import db
from overhave.publication import StashVersionPublisher
from overhave.storage import DraftModel
from overhave.transport import StashPrCreationResponse, StashErrorResponse, StashHttpClientConflictError
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestStashbVersionPublisher:
    """Integration tests for Overhave StashVersion Publisher"""

    @pytest.mark.parametrize("stash_version_publisher", [True], indirect=True)  # тут бы параметр покрасивее назвать
    def test_context_is_none(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.INTERNAL_ERROR
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR

    def test_response_with_error(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.INTERNAL_ERROR
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR

    def test_creation_response(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            stash_version_publisher.send_pull_request.side_effect = StashPrCreationResponse(
                pull_request_url="hoho",
                created_date = datetime.date()
            )
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.CREATED
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.feature.released is True
            assert draft.pr_url == "hoho"
            assert draft.published_at == datetime.date

    def test_stash_error_response(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            stash_response = StashErrorResponse()
            stash_response.duplicate = True
            stash_version_publisher.send_pull_request.side_effect = stash_response
            stash_version_publisher.publish_version(draft_id=test_draft.id)
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.DUPLICATE

    def test_http_conflict(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            stash_version_publisher.send_pull_request.side_effect = StashHttpClientConflictError
            stash_version_publisher.publish_version(draft_id=test_draft.id)
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR

    def test_http_error(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            stash_version_publisher.send_pull_request.side_effect = httpx.HTTPError
            stash_version_publisher.publish_version(draft_id=test_draft.id)
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR
