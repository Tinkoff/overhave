from functools import cache

from prometheus_client import CollectorRegistry

from overhave.metrics import (
    BaseOverhaveMetricContainer,
    EmulationRunOverhaveMetricContainer,
    PublicationOverhaveMetricContainer,
    TestRunOverhaveMetricContainer,
)


def get_collector_registry() -> CollectorRegistry:
    return CollectorRegistry()


@cache
def get_common_metric_container() -> BaseOverhaveMetricContainer:
    return BaseOverhaveMetricContainer(registry=get_collector_registry())


@cache
def get_test_metric_container() -> TestRunOverhaveMetricContainer:
    return TestRunOverhaveMetricContainer(registry=get_collector_registry())


@cache
def get_emulation_metric_container() -> EmulationRunOverhaveMetricContainer:
    return EmulationRunOverhaveMetricContainer(registry=get_collector_registry())


@cache
def get_publication_metric_container() -> PublicationOverhaveMetricContainer:
    return PublicationOverhaveMetricContainer(registry=get_collector_registry())
