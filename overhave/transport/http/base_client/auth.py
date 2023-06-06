from typing import Generator

import httpx
import requests


class BearerAuth(httpx.Auth):
    """Class for Bearer auth_managers pattern."""

    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

    def __call__(self, request: httpx.Request | requests.PreparedRequest) -> httpx.Request | requests.PreparedRequest:
        return next(self.auth_flow(request=request))  # type: ignore
