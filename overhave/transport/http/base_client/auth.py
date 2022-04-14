from typing import Any

import requests


class BearerAuth(requests.auth.AuthBase):
    """Class for Bearer auth_managers pattern."""

    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BearerAuth):
            return False
        return self.token == other.token
