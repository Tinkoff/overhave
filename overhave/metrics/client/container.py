import logging

from prometheus_client import CollectorRegistry, Counter

from overhave.db import DraftStatus, EmulationStatus, TestRunStatus
from overhave.transport import RedisStream

logger = logging.getLogger(__name__)


class OverhaveMetricContainer:
    """Overhave prometheus metric container."""

    def __init__(self, registry: CollectorRegistry):
        self.registry = registry
        self._init_test_run_metrics()
        self._init_publication_metrics()
        self._init_emulation_metrics()
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

    def _init_test_run_metrics(self) -> None:
        self.test_run_tasks_statuses = Counter(
            "test_run_tasks_statuses",
            "Counter for test run statuses",
            labelnames=("status",),
            registry=self.registry,
        )

    def _init_publication_metrics(self) -> None:
        self.publication_tasks_statuses = Counter(
            "publication_tasks_statuses",
            "Counter for publication run statuses",
            labelnames=("status",),
            registry=self.registry,
        )

    def _init_emulation_metrics(self) -> None:
        self.emulation_tasks_statuses = Counter(
            "emulation_tasks_statuses",
            "Counter for emulation statuses",
            labelnames=("status", "port"),
            registry=self.registry,
        )

    def _produce_redis_task(self, task_type: RedisStream) -> None:
        self.produced_redis_tasks.labels(task_type=task_type).inc()

    def _consume_redis_task(self, task_type: RedisStream) -> None:
        self.consumed_redis_tasks.labels(task_type=task_type).inc()

    def produce_test_run_task(self) -> None:
        self._produce_redis_task(task_type=RedisStream.TEST)

    def produce_emulation_run_task(self) -> None:
        self._produce_redis_task(task_type=RedisStream.EMULATION)

    def produce_publication_task(self) -> None:
        self._produce_redis_task(task_type=RedisStream.PUBLICATION)

    def consume_test_run_task(self) -> None:
        self._consume_redis_task(task_type=RedisStream.TEST)

    def consume_emulation_run_task(self) -> None:
        self._consume_redis_task(task_type=RedisStream.EMULATION)

    def consume_publication_task(self) -> None:
        self._consume_redis_task(task_type=RedisStream.PUBLICATION)

    def add_test_run_status(self, status: TestRunStatus) -> None:
        self.test_run_tasks_statuses.labels(status=status).inc()

    def add_publication_task_status(self, status: DraftStatus) -> None:
        self.publication_tasks_statuses.labels(status=status).inc()

    def add_emulation_task_status(self, status: EmulationStatus, port: int | None = None) -> None:
        self.emulation_tasks_statuses.labels(status=status, port=port).inc()
