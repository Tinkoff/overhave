import datetime

import pytest

from overhave import db
from overhave.publication import GitlabVersionPublisher
from overhave.storage import DraftModel
from tests.db_utils import create_test_session, count_queries


@pytest.mark.usefixtures("database")
class TestGitlabVersionPublisher:
    """Integration tests for Overhave GitlabVersion Publisher"""

    def test_without_error(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            gitlab_version_publisher.publish_version(draft_id=test_draft.id)
        with create_test_session() as session:
            new_test_draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert new_test_draft.status is db.DraftStatus.CREATED
            assert new_test_draft.feature.released is True
            assert new_test_draft.pr_url == "hehe"
            assert new_test_draft.published_at == datetime.date

    @pytest.mark.parametrize("should_raise_http", True)
    def test_raise_http(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            gitlab_version_publisher.publish_version(draft_id=test_draft.id)
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR
            #assert draft.traceback

    @pytest.mark.parametrize("should_raise_gitlab", True)
    def test_raise_gitlab(self, gitlab_version_publisher: GitlabVersionPublisher, test_draft: DraftModel) -> None:
        with count_queries(1):
            gitlab_version_publisher.publish_version(draft_id=test_draft.id)
        with create_test_session() as session:
            draft = session.query(db.Draft).filter(db.Draft.id == test_draft.id).one()
            assert draft.status == db.DraftStatus.INTERNAL_ERROR
            # assert draft.traceback