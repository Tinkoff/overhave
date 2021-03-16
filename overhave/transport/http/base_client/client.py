import logging
from json import JSONDecodeError
from typing import Any, Dict, Generic, Mapping, Optional, Union, cast

import requests
import tenacity
from pydantic import BaseModel, ValidationError
from pydantic.main import ModelMetaclass
from requests.auth import AuthBase
from yarl import URL

from overhave.transport.http.base_client.objects import HttpMethod
from overhave.transport.http.base_client.settings import HttpSettingsType

logger = logging.getLogger(__name__)


class BaseHttpClientException(Exception):
    """ Base exception for BaseHttpClient. """


class HttpClientValidationError(BaseHttpClientException):
    """ Model validation error for BaseHttpClient. """


class BaseHttpClient(Generic[HttpSettingsType]):
    """ Base client for HTTP communications. """

    def __init__(self, settings: HttpSettingsType) -> None:
        self._settings = settings

    @staticmethod
    def _parse_or_raise(response: requests.Response, model: ModelMetaclass) -> BaseModel:
        try:
            return cast(BaseModel, model).parse_obj(response.json())
        except (ValueError, ValidationError, JSONDecodeError) as e:
            url = getattr(response, "raw_url", response.url)
            raise HttpClientValidationError(f'Response validation error for "{url}"') from e

    @tenacity.retry(
        reraise=True,
        retry=tenacity.retry_if_exception_type(requests.ConnectionError),
        stop=tenacity.stop_after_attempt(3),
        before_sleep=tenacity.before_sleep_log(logger, logger.level),
        after=tenacity.after_log(logger, logger.level),
    )
    def _make_request(
        self,
        method: HttpMethod,
        url: URL,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes, Mapping[Any, Any]]] = None,
        auth: Optional[AuthBase] = None,
        raise_for_status: bool = True,
    ) -> requests.Response:
        response = requests.request(
            method=method.value,
            url=url.human_repr(),
            params=params,
            json=json,
            data=data,
            auth=auth,
            timeout=self._settings.timeout,
        )
        if raise_for_status:
            response.raise_for_status()
        return response
