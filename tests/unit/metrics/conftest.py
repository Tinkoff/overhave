import pytest
from prometheus_client import CollectorRegistry

from overhave.metrics.client.container import OverhaveMetricContainer


@pytest.fixture()
def registry():
    return CollectorRegistry()


@pytest.fixture()
def container(registry: CollectorRegistry):
    return OverhaveMetricContainer(registry)
