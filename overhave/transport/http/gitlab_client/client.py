import logging

from gitlab.exceptions import GitlabAuthenticationError
from gitlab.v4.objects import ProjectMergeRequest

from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import BaseHttpClientException, HttpClientValidationError
from overhave.transport.http.gitlab_client.models import GitlabMrCreationResponse, GitlabMrRequest
from overhave.transport.http.gitlab_client.settings import OverhaveGitlabClientSettings
from overhave.transport.http.gitlab_client.utils import get_gitlab_python_client

logger = logging.getLogger(__name__)


class BaseGitlabHttpClientException(BaseHttpClientException):
    """Base exception for :class:`GitlabHttpClient`."""


class GitlabInvalidTokenError(BaseGitlabHttpClientException):
    """Exception for situation with invalid token or gitlab url."""


class GitlabHttpClient(BaseHttpClient[OverhaveGitlabClientSettings]):
    """Client for communication with remote Gitlab server."""

    def send_merge_request(
        self, repository_id: str, merge_request: GitlabMrRequest, token: str
    ) -> GitlabMrCreationResponse:
        gitlab_python_client = get_gitlab_python_client(
            url=self._settings.url,
            token_type=self._settings.token_type,
            token=token,
        )
        project = gitlab_python_client.projects.get(repository_id, lazy=True)
        try:
            result = project.mergerequests.create(merge_request.model_dump(by_alias=True))
            logger.debug("Response from GitLab: %s", result)
            if isinstance(result, ProjectMergeRequest):
                return GitlabMrCreationResponse(created_at=result.created_at, web_url=result.web_url)
            raise HttpClientValidationError("Unsupported response: %s", result)
        except GitlabAuthenticationError as e:
            logging.exception("Please verify your token or URL! Maybe they are invalid")
            raise GitlabInvalidTokenError("Please verify your token or URL! Maybe they are invalid") from e
