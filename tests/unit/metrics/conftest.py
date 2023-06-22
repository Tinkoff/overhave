import pytest
from prometheus_client import CollectorRegistry

from overhave.metrics.client.container import (
    BaseOverhaveMetricContainer,
    EmulationRunOverhaveMetricContainer,
    PublicationOverhaveMetricContainer,
    TestRunOverhaveMetricContainer,
)


@pytest.fixture()
def registry():
    return CollectorRegistry()


@pytest.fixture()
def base_container(registry: CollectorRegistry):
    return BaseOverhaveMetricContainer(registry=registry)


@pytest.fixture()
def test_container(registry: CollectorRegistry):
    return TestRunOverhaveMetricContainer(registry=registry)


@pytest.fixture()
def emulation_container(registry: CollectorRegistry):
    return EmulationRunOverhaveMetricContainer(registry=registry)


@pytest.fixture()
def publication_container(registry: CollectorRegistry):
    return PublicationOverhaveMetricContainer(registry=registry)
