from dataclasses import dataclass

from overhave.db import TestReportStatus


@dataclass(frozen=True)
class ReportPresenceResolution:
    """Model for report presence resolution result."""

    exists: bool

    report_status: TestReportStatus | None = None
    s3_enabled: bool = False

    @property
    def not_ready(self) -> bool:
        return self.s3_enabled and not self.exists and self.report_status is TestReportStatus.GENERATED
