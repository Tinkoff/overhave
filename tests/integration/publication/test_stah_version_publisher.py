from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from overhave.publication import StashVersionPublisher


class TestStashbVersionPublisher:
    """Integration tests for Overhave StashVersion Publisher"""

    def test_publish_version(self, stash_version_publisher: StashVersionPublisher, draft_id: int) -> None:
        stash_version_publisher.publish_version(draft_id=draft_id)