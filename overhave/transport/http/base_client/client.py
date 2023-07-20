import logging
from typing import Any, Generic, Mapping, cast

import httpx
import tenacity
from pydantic import BaseModel, ValidationError
from pydantic._internal._model_construction import ModelMetaclass

from overhave.transport.http.base_client.objects import HttpMethod
from overhave.transport.http.base_client.settings import HttpSettingsType

logger = logging.getLogger(__name__)


class BaseHttpClientException(Exception):
    """Base exception for BaseHttpClient."""


class HttpClientValidationError(BaseHttpClientException):
    """Model validation error for BaseHttpClient."""


class BaseHttpClient(Generic[HttpSettingsType]):
    """Base client for HTTP communications."""

    def __init__(self, settings: HttpSettingsType) -> None:
        self._settings = settings

    @staticmethod
    def _parse_or_raise(response: httpx.Response, model: ModelMetaclass) -> BaseModel:
        try:
            return cast(BaseModel, model).model_validate(response.json())
        except (ValueError, ValidationError) as e:
            url = getattr(response, "raw_url", response.url)
            raise HttpClientValidationError(f'Response validation error for "{url}"') from e

    @tenacity.retry(
        reraise=True,
        retry=tenacity.retry_if_exception_type(httpx.ConnectError),
        stop=tenacity.stop_after_attempt(3),
        before_sleep=tenacity.before_sleep_log(logger, logger.level),
        after=tenacity.after_log(logger, logger.level),
    )
    def _make_request(
        self,
        method: HttpMethod,
        url: httpx.URL,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: str | bytes | Mapping[Any, Any] | None = None,
        auth: httpx.Auth | None = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        response = httpx.request(
            method=str(method.value),
            url=str(url),
            params=params,
            json=json,
            data=data,  # type: ignore
            auth=auth,
            timeout=self._settings.timeout,
        )
        if raise_for_status:
            response.raise_for_status()
        return response
