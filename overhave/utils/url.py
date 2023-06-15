import httpx


def make_url(value: str | None) -> httpx.URL | None:
    if isinstance(value, str):
        return httpx.URL(value)
    return value
