import allure
import httpx
import pytest

from overhave import db
from overhave.publication import StashVersionPublisher
from overhave.storage import DraftModel
from overhave.transport import StashErrorResponse, StashHttpClientConflictError, StashPrCreationResponse
from overhave.transport.http.stash_client.models import StashRequestError
from overhave.utils import get_current_time
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestStashbVersionPublisher:
    """Integration tests for Overhave StashVersion Publisher."""

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
        with count_queries(2):
            stash_version_publisher._client.send_pull_request.return_value = StashPrCreationResponse(  # type: ignore
                pull_request_url="hoho",
                createdDate=get_current_time(),
                updatedDate=get_current_time(),
                open=True,
            )
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.CREATED
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.feature.released is True
            assert draft.pr_url == "hoho"

    def test_stash_error_response(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(2):
            error = StashRequestError(context="123", message="111", exceptionName="DuplicatePullRequestException")
            stash_response = StashErrorResponse(errors=[error])
            stash_version_publisher._client.send_pull_request.return_value = stash_response  # type: ignore
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.DUPLICATE
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.DUPLICATE

    def test_http_conflict(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(2):
            error = StashHttpClientConflictError()
            stash_version_publisher._client.send_pull_request.side_effect = error  # type: ignore
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.DUPLICATE
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.DUPLICATE

    def test_http_error(self, stash_version_publisher: StashVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            stash_version_publisher._client.send_pull_request.side_effect = httpx.HTTPError("lolkek")  # type: ignore
            draft_status = stash_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.INTERNAL_ERROR
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR
