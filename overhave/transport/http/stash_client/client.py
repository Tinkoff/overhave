import logging
from typing import cast

from overhave.transport.http.base_client import BaseHttpClient, BearerAuth, HttpClientValidationError, HttpMethod
from overhave.transport.http.stash_client.models import STASH_RESPONSE_MODELS, AnyStashResponseModel, StashPrRequest
from overhave.transport.http.stash_client.settings import OverhaveStashClientSettings

logger = logging.getLogger(__name__)


class StashHttpClient(BaseHttpClient[OverhaveStashClientSettings]):
    """ Client for communication with remote Bitbucket server. """

    def send_pr(self, pull_request: StashPrRequest) -> AnyStashResponseModel:
        url = self._settings.get_pr_url(
            project_key=pull_request.target_branch.repository.project.key,
            repository_name=pull_request.target_branch.repository.name,
        )
        response = self._make_request(
            method=HttpMethod.POST,
            url=url,
            json=pull_request.dict(by_alias=True),
            auth=BearerAuth(self._settings.auth_token),
        )
        for model in STASH_RESPONSE_MODELS:
            try:
                logger.debug("Trying to parse '%s'...", model)
                return cast(AnyStashResponseModel, self._parse_or_raise(response, model))
            except HttpClientValidationError:
                logger.debug("Could not convert response to '%s'!", model, exc_info=True)
        raise HttpClientValidationError(
            f"Could not parse Stash response while trying to create pull-request!\nResponse: {response.json()}"
        )
