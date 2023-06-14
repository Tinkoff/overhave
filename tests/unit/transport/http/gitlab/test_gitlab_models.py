import datetime

import pytest
from pydantic import ValidationError

from overhave.transport import GitlabMrCreationResponse


class TestGitlabHttpClientModels:
    """Unit tests for :class:`GitlabHttpClient` models."""

    def test_mr_creation_response(self) -> None:
        response: GitlabMrCreationResponse = GitlabMrCreationResponse.parse_obj(
            {
                "id": 1,
                "iid": 1,
                "project_id": 3,
                "title": "test1",
                "description": "fixed login page css paddings",
                "state": "merged",
                "created_at": "2017-04-29T08:46:00Z",
                "updated_at": "2017-04-29T08:46:00Z",
                "target_branch": "master",
                "source_branch": "test1",
                "upvotes": 0,
                "downvotes": 0,
                "author": {
                    "id": 1,
                    "name": "Administrator",
                    "username": "admin",
                    "state": "active",
                    "avatar_url": None,
                    "web_url": "https://gitlab.example.com/admin",
                },
                "assignee": {
                    "id": 1,
                    "name": "Administrator",
                    "username": "admin",
                    "state": "active",
                    "avatar_url": None,
                    "web_url": "https://gitlab.example.com/admin",
                },
                "source_project_id": 2,
                "target_project_id": 3,
                "labels": ["Community contribution", "Manage"],
                "draft": False,
                "work_in_progress": False,
                "milestone": {
                    "id": 5,
                    "iid": 1,
                    "project_id": 3,
                    "title": "v2.0",
                    "description": "Assumenda aut placeat expedita exercitationem labore sunt enim earum.",
                    "state": "closed",
                    "created_at": "2015-02-02T19:49:26.013Z",
                    "updated_at": "2015-02-02T19:49:26.013Z",
                    "due_date": "2018-09-22",
                    "start_date": "2018-08-08",
                    "web_url": "https://gitlab.example.com/my-group/my-project/milestones/1",
                },
                "merge_when_pipeline_succeeds": True,
                "merge_status": "can_be_merged",
                "merge_error": None,
                "sha": "8888888888888888888888888888888888888888",
                "merge_commit_sha": None,
                "squash_commit_sha": None,
                "user_notes_count": 1,
                "discussion_locked": None,
                "should_remove_source_branch": True,
                "force_remove_source_branch": False,
                "allow_collaboration": False,
                "allow_maintainer_to_push": False,
                "web_url": "http://gitlab.example.com/my-group/my-project/merge_requests/1",
                "references": {"short": "!1", "relative": "!1", "full": "my-group/my-project!1"},
                "time_stats": {
                    "time_estimate": 0,
                    "total_time_spent": 0,
                    "human_time_estimate": None,
                    "human_total_time_spent": None,
                },
                "squash": False,
                "subscribed": False,
                "changes_count": "1",
                "merged_by": {
                    "id": 87854,
                    "name": "Douwe Maan",
                    "username": "DouweM",
                    "state": "active",
                    "avatar_url": "https://gitlab.example.com/uploads/-/system/user/avatar/87854/avatar.png",
                    "web_url": "https://gitlab.com/DouweM",
                },
                "merged_at": "2018-09-07T11:16:17.520Z",
                "closed_by": None,
                "closed_at": None,
                "latest_build_started_at": "2018-09-07T07:27:38.472Z",
                "latest_build_finished_at": "2018-09-07T08:07:06.012Z",
                "first_deployed_to_production_at": None,
                "pipeline": {
                    "id": 29626725,
                    "sha": "2be7ddb704c7b6b83732fdd5b9f09d5a397b5f8f",
                    "ref": "patch-28",
                    "status": "success",
                    "web_url": "https://gitlab.example.com/my-group/my-project/pipelines/29626725",
                },
                "diff_refs": {
                    "base_sha": "c380d3acebd181f13629a25d2e2acca46ffe1e00",
                    "head_sha": "2be7ddb704c7b6b83732fdd5b9f09d5a397b5f8f",
                    "start_sha": "c380d3acebd181f13629a25d2e2acca46ffe1e00",
                },
                "diverged_commits_count": 2,
                "task_completion_status": {"count": 0, "completed_count": 0},
            }
        )

        assert response.web_url == "http://gitlab.example.com/my-group/my-project/merge_requests/1"
        assert response.created_at == datetime.datetime(2017, 4, 29, 8, 46, 0, tzinfo=datetime.timezone.utc)

    def test_bullshit_mr_creation_response(self) -> None:
        with pytest.raises(ValidationError):
            GitlabMrCreationResponse.parse_obj(
                {"state": "merged", "created_at": "2017-04-29T08:46:00Z", "updated_at": "2017-04-29T08:46:00Z"}
            )
