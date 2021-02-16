from functools import lru_cache

from overhave.factory.proxy_factory import ProxyFactory


@lru_cache(maxsize=None)
def get_proxy_factory() -> ProxyFactory:
    return ProxyFactory()
