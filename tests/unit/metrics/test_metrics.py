import pytest

from overhave.db import DraftStatus, TestRunStatus
from overhave.metrics.client.container import OverhaveMetricContainer


class TestMetrics:
    """Test for overhave metrics."""

    def test_run_task(self, container: OverhaveMetricContainer) -> None:
        container.add_test_run_task()
        container.add_test_run_task()
        assert list(container.test_run_tasks.collect())[0].samples[0].value == 2
        container.add_publication_task()
        container.add_publication_task()
        container.add_publication_task()
        assert list(container.publication_tasks.collect())[0].samples[0].value == 3

    @pytest.mark.parametrize("test_run_status", TestRunStatus)
    def test_add_test_run_status(self, container: OverhaveMetricContainer, test_run_status: TestRunStatus) -> None:
        container.add_test_run_status(status=test_run_status)
        sample = list(container.test_run_tasks_statuses.collect())[0].samples[0]
        assert sample.value == 1
        assert sample.labels["status"] == test_run_status

    @pytest.mark.parametrize("draft_status", DraftStatus)
    def test_add_publication_status(self, container: OverhaveMetricContainer, draft_status: DraftStatus) -> None:
        container.add_publication_task_status(status=draft_status)
        container.add_publication_task_status(status=draft_status)
        sample = list(container.publication_tasks_statuses.collect())[0].samples[0]
        assert sample.value == 2
        assert sample.labels["status"] == draft_status
