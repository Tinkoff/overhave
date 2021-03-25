import abc
from functools import cached_property, lru_cache
from typing import Optional, Union

from overhave.factory import IAdminFactory, ITestExecutionFactory
from overhave.pytest_plugin.config_injector import ConfigInjector
from overhave.pytest_plugin.plugin_resolver import PluginResolver

AnyProxyFactory = Union[IAdminFactory, ITestExecutionFactory]


class IProxyManager(abc.ABC):
    """ Abstract class for proxy manager. """

    @property
    @abc.abstractmethod
    def injector(self) -> ConfigInjector:
        pass

    @abc.abstractmethod
    def set_factory(self, factory: AnyProxyFactory) -> None:
        pass

    @property
    @abc.abstractmethod
    def factory(self) -> AnyProxyFactory:
        pass

    @property
    @abc.abstractmethod
    def has_factory(self) -> bool:
        pass

    @abc.abstractmethod
    def clear_factory(self) -> None:
        pass

    @abc.abstractmethod
    def patch_pytest(self) -> None:
        pass

    @property
    @abc.abstractmethod
    def plugin_resolver(self) -> PluginResolver:
        pass

    @property
    @abc.abstractmethod
    def pytest_patched(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def collection_prepared(self) -> bool:
        pass

    @abc.abstractmethod
    def supply_injector_for_collection(self) -> None:
        pass


class BaseProxyManagerException(Exception):
    """ Base exception for :class:`ProxyManager`. """


class FactoryAlreadyDefinedError(BaseProxyManagerException):
    """ Exception for situation with already defined `factory`. """


class FactoryNotDefinedError(BaseProxyManagerException):
    """ Exception for situation with not defined `factory`. """


class ProxyManager(IProxyManager):
    """ Manager for application factory resolution and usage, based on proxy-object pattern. """

    def __init__(self) -> None:
        self._factory: Optional[AnyProxyFactory] = None
        self._pytest_patched = False
        self._collection_prepared = False

    @cached_property
    def _injector(self) -> ConfigInjector:
        return ConfigInjector()

    @property
    def injector(self) -> ConfigInjector:
        return self._injector

    def set_factory(self, factory: AnyProxyFactory) -> None:
        if self._factory is not None:
            raise FactoryAlreadyDefinedError("Factory is not nullable!")
        self._factory = factory

    @property
    def factory(self) -> AnyProxyFactory:
        if self._factory is None:
            raise FactoryNotDefinedError("Factory is nullable!")
        return self._factory

    def clear_factory(self) -> None:
        self._factory = None

    @property
    def has_factory(self) -> bool:
        return self._factory is not None

    def patch_pytest(self) -> None:
        if not self._pytest_patched:
            self._injector.patch_pytestbdd_prefixes(
                custom_step_prefixes=self.factory.context.language_settings.step_prefixes
            )
            self._pytest_patched = True

    @cached_property
    def _plugin_resolver(self) -> PluginResolver:
        return PluginResolver(self.factory.context.file_settings)

    @property
    def plugin_resolver(self) -> PluginResolver:
        return self._plugin_resolver

    @property
    def pytest_patched(self) -> bool:
        return self._pytest_patched

    @property
    def collection_prepared(self) -> bool:
        return self._collection_prepared

    def supply_injector_for_collection(self) -> None:
        if not self._collection_prepared:
            self._injector.supplement_components(
                file_settings=self.factory.context.file_settings,
                step_collector=self.factory.step_collector,
                test_runner=self.factory.test_runner,
                feature_extractor=self.factory.feature_extractor,
            )
            self._collection_prepared = True


@lru_cache(maxsize=None)
def get_proxy_manager() -> IProxyManager:
    return ProxyManager()
