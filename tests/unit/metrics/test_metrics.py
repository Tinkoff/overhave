import pytest
from prometheus_client import Counter
from prometheus_client.samples import Sample

from overhave.db import DraftStatus, EmulationStatus, TestRunStatus
from overhave.metrics.client.container import (
    BaseOverhaveMetricContainer,
    EmulationRunOverhaveMetricContainer,
    PublicationOverhaveMetricContainer,
    TestRunOverhaveMetricContainer,
)
from overhave.transport import RedisStream


def get_sample_from_counter(counter: Counter) -> Sample:
    return list(counter.collect())[0].samples[0]


class TestMetrics:
    """Test for overhave metrics."""

    def test_produce_test_run_task(self, base_container: BaseOverhaveMetricContainer) -> None:
        base_container.produce_redis_task(task_type=RedisStream.TEST.value)
        base_container.produce_redis_task(task_type=RedisStream.TEST.value)
        sample = get_sample_from_counter(base_container.produced_redis_tasks)
        assert sample.value == 2
        assert sample.labels["task_type"] == RedisStream.TEST.value

    def test_produce_emulation_run_task(self, base_container: BaseOverhaveMetricContainer) -> None:
        base_container.produce_redis_task(task_type=RedisStream.EMULATION.value)
        base_container.produce_redis_task(task_type=RedisStream.EMULATION.value)
        base_container.produce_redis_task(task_type=RedisStream.EMULATION.value)
        sample = get_sample_from_counter(base_container.produced_redis_tasks)
        assert sample.value == 3
        assert sample.labels["task_type"] == RedisStream.EMULATION.value

    def test_produce_publication_task(self, base_container: BaseOverhaveMetricContainer) -> None:
        base_container.produce_redis_task(task_type=RedisStream.PUBLICATION.value)
        sample = get_sample_from_counter(base_container.produced_redis_tasks)
        assert sample.value == 1
        assert sample.labels["task_type"] == RedisStream.PUBLICATION.value

    def test_consume_test_run_task(self, base_container: BaseOverhaveMetricContainer) -> None:
        base_container.consume_redis_task(task_type=RedisStream.TEST.value)
        base_container.consume_redis_task(task_type=RedisStream.TEST.value)
        sample = get_sample_from_counter(base_container.consumed_redis_tasks)
        assert sample.value == 2
        assert sample.labels["task_type"] == RedisStream.TEST.value

    def test_consume_emulation_run_task(self, base_container: BaseOverhaveMetricContainer) -> None:
        base_container.consume_redis_task(task_type=RedisStream.EMULATION.value)
        base_container.consume_redis_task(task_type=RedisStream.EMULATION.value)
        base_container.consume_redis_task(task_type=RedisStream.EMULATION.value)
        sample = get_sample_from_counter(base_container.consumed_redis_tasks)
        assert sample.value == 3
        assert sample.labels["task_type"] == RedisStream.EMULATION.value

    def test_consume_publication_task(self, base_container: BaseOverhaveMetricContainer) -> None:
        base_container.consume_redis_task(task_type=RedisStream.PUBLICATION.value)
        sample = get_sample_from_counter(base_container.consumed_redis_tasks)
        assert sample.value == 1
        assert sample.labels["task_type"] == RedisStream.PUBLICATION.value

    @pytest.mark.parametrize("test_run_status", TestRunStatus)
    def test_add_test_run_status(
        self, test_container: TestRunOverhaveMetricContainer, test_run_status: TestRunStatus
    ) -> None:
        test_container.add_test_run_status(status=test_run_status.value)
        sample = get_sample_from_counter(test_container.test_run_tasks_statuses)
        assert sample.value == 1
        assert sample.labels["status"] == test_run_status.value

    @pytest.mark.parametrize("draft_status", DraftStatus)
    def test_add_publication_status(
        self, publication_container: PublicationOverhaveMetricContainer, draft_status: DraftStatus
    ) -> None:
        publication_container.add_publication_task_status(status=draft_status.value)
        publication_container.add_publication_task_status(status=draft_status.value)
        sample = get_sample_from_counter(publication_container.publication_tasks_statuses)
        assert sample.value == 2
        assert sample.labels["status"] == draft_status.value

    @pytest.mark.parametrize("emulation_status", EmulationStatus)
    @pytest.mark.parametrize("port", [8000, 8001, 8002])
    def test_add_emulation_status(
        self, emulation_container: EmulationRunOverhaveMetricContainer, emulation_status: EmulationStatus, port: int
    ) -> None:
        emulation_container.add_emulation_task_status(status=emulation_status.value, port=port)
        emulation_container.add_emulation_task_status(status=emulation_status.value, port=port)
        sample = get_sample_from_counter(emulation_container.emulation_tasks_statuses)
        assert sample.value == 2
        assert sample.labels["status"] == emulation_status.value
        assert sample.labels["port"] == str(port)
