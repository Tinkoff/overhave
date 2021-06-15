import logging
from http import HTTPStatus
from typing import cast

from overhave.transport.http import BaseHttpClient
from overhave.transport.http.base_client import (
    BaseHttpClientException,
    BearerAuth,
    HttpClientValidationError,
    HttpMethod,
)
from overhave.transport.http.gitlab_client.models import GITLAB_RESPONSE_MODELS, AnyGitlabResponseModel, GitlabMrRequest
from overhave.transport.http.gitlab_client.settings import OverhaveGitlabClientSettings

logger = logging.getLogger(__name__)


class BaseGitlabHttpClientException(BaseHttpClientException):
    """ Base exception for :class:`GitlabHttpClient`. """


class GitlabHttpClientConflictError(BaseGitlabHttpClientException):
    """ Exception for situation with `HTTPStatus.CONFLICT` response.status_code. """


class GitlabHttpClient(BaseHttpClient[OverhaveGitlabClientSettings]):
    """ Client for communication with remote Gitlab server. """

    def send_merge_request(self, merge_request: GitlabMrRequest) -> AnyGitlabResponseModel:
        url = self._settings.get_mr_url(merge_request.target_branch.id)
        response = self._make_request(
            method=HttpMethod.POST,
            url=url,
            json=merge_request.dict(by_alias=True),
            auth=BearerAuth(self._settings.auth_token),
            raise_for_status=False,
        )
        if response.status_code == HTTPStatus.CONFLICT:
            raise GitlabHttpClientConflictError("Got conflict when trying to send merge-request!")
        response.raise_for_status()
        for model in GITLAB_RESPONSE_MODELS:
            try:
                logger.debug("Trying to parse '%s'...", model)
                return cast(AnyGitlabResponseModel, self._parse_or_raise(response, model))
            except HttpClientValidationError:
                logger.debug("Could not convert response to '%s'!", model, exc_info=True)
        raise HttpClientValidationError(
            f"Could not parse Gitlab response while trying to create merge-request!\nResponse: {response.json()}"
        )
