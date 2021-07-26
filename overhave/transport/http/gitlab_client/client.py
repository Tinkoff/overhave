import logging
from typing import Any

import gitlab

from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import BaseHttpClientException
from overhave.transport.http.base_client.objects import HttpMethod
from overhave.transport.http.gitlab_client.models import GitlabMrRequest
from overhave.transport.http.gitlab_client.settings import OverhaveGitlabClientSettings

logger = logging.getLogger(__name__)


class BaseGitlabHttpClientException(BaseHttpClientException):
    """ Base exception for :class:`GitlabHttpClient`. """


class GitlabHttpClientConflictError(BaseGitlabHttpClientException):
    """ Exception for situation with `HTTPStatus.CONFLICT` response.status_code. """


class GitlabInvalidTokenError(BaseGitlabHttpClientException):
    """ Exception for situation with invalid token or gitlab url. """


class GitlabHttpClient(BaseHttpClient[OverhaveGitlabClientSettings]):
    """ Client for communication with remote Gitlab server. """

    def send_merge_request(self, merge_request: GitlabMrRequest) -> Any:
        response = self._make_request(
            HttpMethod.POST,
            self._settings.get_token_url,
            params={
                "initiator": self._settings.initiator,
                "id": 0,
                "vault_server_name": self._settings.vault_server_name,
            },
        )
        gl = gitlab.Gitlab(self._settings.url.human_repr(), oauth_token=response.json()["token"])
        project = gl.projects.get(self._settings.repository_id, lazy=True)
        try:
            return project.mergerequests.create(merge_request.dict(by_alias=True))
        except Exception:
            logging.exception("Please verify your token or URL! Maybe they are invalid")
            raise GitlabInvalidTokenError("Please verify your token or URL! Maybe they are invalid")
