from functools import lru_cache

from overhave.factory.components import (
    AdminFactory,
    EmulationFactory,
    IAdminFactory,
    PublicationFactory,
    TestExecutionFactory,
)


@lru_cache(maxsize=None)
def get_admin_factory() -> IAdminFactory:
    return AdminFactory()


@lru_cache(maxsize=None)
def get_test_execution_factory() -> TestExecutionFactory:
    return TestExecutionFactory()


@lru_cache(maxsize=None)
def get_publication_factory() -> PublicationFactory:
    return PublicationFactory()


@lru_cache(maxsize=None)
def get_emulation_factory() -> EmulationFactory:
    return EmulationFactory()
