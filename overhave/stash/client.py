import logging
from typing import Any

import requests.auth
import tenacity
from pydantic import ValidationError

from overhave.stash.errors import StashValidationError
from overhave.stash.models import STASH_RESPONSE_MODELS, AnyStashResponseModel, StashPrRequest
from overhave.stash.settings import OverhaveStashClientSettings

logger = logging.getLogger(__name__)


class _BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _BearerAuth):
            return False
        return self.token == other.token


class StashClient:
    """ Class for communcation with remote Bitbucket server. """

    def __init__(self, settings: OverhaveStashClientSettings):
        self._settings = settings

    @tenacity.retry(
        reraise=True,
        retry=tenacity.retry_if_exception_type(requests.ConnectionError),
        stop=tenacity.stop_after_attempt(3),
        before_sleep=tenacity.before_sleep_log(logger, logger.level),
        after=tenacity.after_log(logger, logger.level),
    )
    def send_pr(self, pull_request: StashPrRequest) -> AnyStashResponseModel:
        url = self._settings.get_pr_url(
            project_key=pull_request.target_branch.repository.project.key,
            repository_name=pull_request.target_branch.repository.name,
        )
        response = requests.post(
            url.human_repr(), json=pull_request.dict(by_alias=True), auth=_BearerAuth(self._settings.auth_token)
        )
        data = response.json()
        for model in STASH_RESPONSE_MODELS:
            try:
                logger.debug("Trying to parse '%s'...", model)
                return model.parse_obj(data)  # type: ignore
            except ValidationError:
                logger.debug("Could not convert response to '%s'!", model, exc_info=True)
        raise StashValidationError(
            f"Could not parse Stash response while trying to create pull-request!\nResponse: {data}"
        )
