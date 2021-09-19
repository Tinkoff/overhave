from functools import cache

from overhave.factory.components import (
    AdminFactory,
    EmulationFactory,
    IAdminFactory,
    IEmulationFactory,
    IPublicationFactory,
    ISynchronizerFactory,
    ITestExecutionFactory,
    PublicationFactory,
    SynchronizerFactory,
    TestExecutionFactory,
)


@cache
def get_admin_factory() -> IAdminFactory:
    return AdminFactory()


@cache
def get_test_execution_factory() -> ITestExecutionFactory:
    return TestExecutionFactory()


@cache
def get_publication_factory() -> IPublicationFactory:
    return PublicationFactory()


@cache
def get_emulation_factory() -> IEmulationFactory:
    return EmulationFactory()


@cache
def get_synchronizer_factory() -> ISynchronizerFactory:
    return SynchronizerFactory()
