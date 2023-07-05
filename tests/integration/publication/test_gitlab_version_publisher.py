import allure
import pytest

from overhave import db
from overhave.publication import GitlabVersionPublisher
from overhave.storage import DraftModel
from tests.db_utils import count_queries, create_test_session


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("test_severity", [allure.severity_level.NORMAL], indirect=True)
@pytest.mark.parametrize("test_user_role", [db.Role.user], indirect=True)
class TestGitlabVersionPublisher:
    """Integration tests for Overhave GitlabVersion Publisher."""

    @pytest.mark.parametrize("mocked_gitlab_client", [True], indirect=True)
    def test_without_error(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(2):
            draft_status = gitlab_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.CREATED
        with create_test_session() as session:
            new_test_draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert new_test_draft.status == db.DraftStatus.CREATED
            assert new_test_draft.feature.released is True
            assert new_test_draft.pr_url == "hehe"

    @pytest.mark.parametrize("gitlab_version_publisher", [True], indirect=True)
    @pytest.mark.parametrize("mocked_gitlab_client", [True], indirect=True)
    def test_none_context(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            draft_status = gitlab_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.INTERNAL_ERROR

    @pytest.mark.parametrize("should_raise_http", [True], indirect=True)
    def test_raise_http(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            draft_status = gitlab_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.INTERNAL_ERROR
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR

    @pytest.mark.parametrize("should_raise_gitlab", [True], indirect=True)
    def test_raise_gitlab(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(2):
            draft_status = gitlab_version_publisher.publish_version(draft_id=test_draft.id)
            assert draft_status == db.DraftStatus.DUPLICATE
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.DUPLICATE
