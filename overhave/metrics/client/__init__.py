import logging

from prometheus_client import CollectorRegistry

from overhave.metrics.client.container import (
    BaseOverhaveMetricContainer,
    EmulationRunOverhaveMetricContainer,
    PublicationOverhaveMetricContainer,
    TestRunOverhaveMetricContainer,
)
from overhave.metrics.client.settings import MetricSettings

logger = logging.getLogger(__name__)


class AllMetricsContainer(
    TestRunOverhaveMetricContainer,
    EmulationRunOverhaveMetricContainer,
    PublicationOverhaveMetricContainer,
):
    """Class for all containers."""

    def __init__(self, registry: CollectorRegistry):
        super().__init__(registry)


def create_metric_container() -> BaseOverhaveMetricContainer:
    registry = CollectorRegistry()
    mapping = {
        MetricSettings.Type.COMMON: (lambda: BaseOverhaveMetricContainer(registry)),
        MetricSettings.Type.TEST: (lambda: TestRunOverhaveMetricContainer(registry)),
        MetricSettings.Type.EMULATION: (lambda: EmulationRunOverhaveMetricContainer(registry)),
        MetricSettings.Type.PUBLICATION: (lambda: PublicationOverhaveMetricContainer(registry)),
    }
    container_getter = mapping[MetricSettings().type]
    return container_getter()


METRICS: AllMetricsContainer = create_metric_container()  # type: ignore[assignment]
