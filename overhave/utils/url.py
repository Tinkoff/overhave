from typing import Optional

from yarl import URL


def make_url(value: Optional[str]) -> Optional[URL]:
    if isinstance(value, str):
        return URL(value)
    return value
