import logging
from typing import Any

import gitlab

from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import BaseHttpClientException
from overhave.transport.http.gitlab_client.models import GitlabMrRequest
from overhave.transport.http.gitlab_client.settings import OverhaveGitlabClientSettings

logger = logging.getLogger(__name__)


class BaseGitlabHttpClientException(BaseHttpClientException):
    """ Base exception for :class:`GitlabHttpClient`. """


class GitlabHttpClientConflictError(BaseGitlabHttpClientException):
    """ Exception for situation with `HTTPStatus.CONFLICT` response.status_code. """


class GitlabHttpClient(BaseHttpClient[OverhaveGitlabClientSettings]):
    """ Client for communication with remote Gitlab server. """

    def send_merge_request(self, merge_request: GitlabMrRequest) -> Any:
        url = self._settings.url
        gl = gitlab.Gitlab(url.human_repr(), private_token=self._settings.auth_token)
        project = gl.projects.get(self._settings.repository_id, lazy=True)
        return project.mergerequests.create(merge_request.dict(by_alias=True))
