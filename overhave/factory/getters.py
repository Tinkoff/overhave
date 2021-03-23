from functools import lru_cache

from overhave.factory.components import (
    AdminFactory,
    EmulationFactory,
    IAdminFactory,
    IEmulationFactory,
    IPublicationFactory,
    ITestExecutionFactory,
    PublicationFactory,
    TestExecutionFactory,
)


@lru_cache(maxsize=None)
def get_admin_factory() -> IAdminFactory:
    return AdminFactory()


@lru_cache(maxsize=None)
def get_test_execution_factory() -> ITestExecutionFactory:
    return TestExecutionFactory()


@lru_cache(maxsize=None)
def get_publication_factory() -> IPublicationFactory:
    return PublicationFactory()


@lru_cache(maxsize=None)
def get_emulation_factory() -> IEmulationFactory:
    return EmulationFactory()
