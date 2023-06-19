import logging

from prometheus_client import CollectorRegistry

from overhave.metrics.client.container import OverhaveMetricContainer

logger = logging.getLogger(__name__)


def create_metric_container() -> OverhaveMetricContainer:
    return OverhaveMetricContainer(CollectorRegistry())


METRICS = create_metric_container()
