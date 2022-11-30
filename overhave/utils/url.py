from typing import Optional

import httpx


def make_url(value: Optional[str]) -> Optional[httpx.URL]:
    if isinstance(value, str):
        return httpx.URL(value)
    return value
