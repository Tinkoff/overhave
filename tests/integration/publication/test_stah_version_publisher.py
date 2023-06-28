import httpx
import pytest

from overhave.publication import StashVersionPublisher
from overhave.transport import StashPrCreationResponse, StashErrorResponse, StashHttpClientConflictError


@pytest.mark.usefixtures("database")
class TestStashbVersionPublisher:
    """Integration tests for Overhave StashVersion Publisher"""


    def test_publish_version2(self, stash_version_publisher: StashVersionPublisher, draft_id: int) -> None:
        stash_version_publisher.send_pull_request.side_effect = StashPrCreationResponse()
        stash_version_publisher.publish_version(draft_id=draft_id)

    def test_publish_version3(self, stash_version_publisher: StashVersionPublisher, draft_id: int) -> None:
        stash_version_publisher.send_pull_request.side_effect = StashErrorResponse()
        stash_version_publisher.publish_version(draft_id=draft_id)

    def test_publish_version4(self, stash_version_publisher: StashVersionPublisher, draft_id: int) -> None:
        stash_version_publisher.send_pull_request.side_effect = StashHttpClientConflictError
        stash_version_publisher.publish_version(draft_id=draft_id)

    def test_publish_version5(self, stash_version_publisher: StashVersionPublisher, draft_id: int) -> None:
        stash_version_publisher.send_pull_request.side_effect = httpx.HTTPError
        stash_version_publisher.publish_version(draft_id=draft_id)