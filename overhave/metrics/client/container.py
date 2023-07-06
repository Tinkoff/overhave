import logging

from prometheus_client import CollectorRegistry, Counter

logger = logging.getLogger(__name__)


class BaseOverhaveMetricContainer:
    """Base prometheus overhave metric container. Contains common metrics."""

    def __init__(self, registry: CollectorRegistry):
        self.registry = registry
        self._init_redis_metrics()

    def _init_redis_metrics(self) -> None:
        self.produced_redis_tasks = Counter(
            "produced_redis_tasks",
            "How many redis tasks have been produced",
            labelnames=("task_type",),
            registry=self.registry,
        )
        self.consumed_redis_tasks = Counter(
            "consumed_redis_tasks",
            "How many redis tasks have been consumed",
            labelnames=("task_type",),
            registry=self.registry,
        )

    def produce_redis_task(self, task_type: str) -> None:
        self.produced_redis_tasks.labels(task_type=task_type).inc()

    def consume_redis_task(self, task_type: str) -> None:
        self.consumed_redis_tasks.labels(task_type=task_type).inc()


class TestRunOverhaveMetricContainer(BaseOverhaveMetricContainer):
    """Overhave prometheus metric container for test runs."""

    __test__ = False

    def __init__(self, registry: CollectorRegistry):
        super().__init__(registry=registry)
        self._init_test_run_metrics()

    def _init_test_run_metrics(self) -> None:
        self.test_run_tasks_statuses = Counter(
            "test_run_tasks_statuses",
            "Counter for test run statuses",
            labelnames=("status",),
            registry=self.registry,
        )

    def add_test_run_status(self, status: str) -> None:
        self.test_run_tasks_statuses.labels(status=status).inc()


class EmulationRunOverhaveMetricContainer(BaseOverhaveMetricContainer):
    """Overhave prometheus metric container for emulation runs."""

    def __init__(self, registry: CollectorRegistry):
        super().__init__(registry=registry)
        self._init_emulation_metrics()

    def _init_emulation_metrics(self) -> None:
        self.emulation_tasks_statuses = Counter(
            "emulation_tasks_statuses",
            "Counter for emulation statuses",
            labelnames=("status", "port"),
            registry=self.registry,
        )

    def add_emulation_task_status(self, status: str, port: int | None = None) -> None:
        self.emulation_tasks_statuses.labels(status=status, port=port).inc()


class PublicationOverhaveMetricContainer(BaseOverhaveMetricContainer):
    """Overhave prometheus metric container for publications."""

    def __init__(self, registry: CollectorRegistry):
        super().__init__(registry=registry)
        self._init_publication_metrics()

    def _init_publication_metrics(self) -> None:
        self.publication_tasks_statuses = Counter(
            "publication_tasks_statuses",
            "Counter for publication run statuses",
            labelnames=("status",),
            registry=self.registry,
        )

    def add_publication_task_status(self, status: str) -> None:
        self.publication_tasks_statuses.labels(status=status).inc()
