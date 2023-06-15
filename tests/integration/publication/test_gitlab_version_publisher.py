from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave.publication import GitlabVersionPublisher


class TestGitlabVersionPublisher:
    """Integration tests for Overhave GitlabVersion Publisher"""

    def test_publish_version(self, gitlab_version_publisher: GitlabVersionPublisher, draft_id: int) -> None:
        gitlab_version_publisher.publish_version(draft_id=draft_id)