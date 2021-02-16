from functools import lru_cache
from typing import NewType

from overhave.factory.proxy_factory import ProxyFactory

OverhaveFactoryType = NewType('OverhaveFactoryType', ProxyFactory)


@lru_cache(maxsize=None)
def get_proxy_factory() -> OverhaveFactoryType:
    return OverhaveFactoryType(ProxyFactory())
