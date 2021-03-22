from typing import Optional

from pydantic import BaseModel

from overhave.db import TestReportStatus


class ReportPresenceResolution(BaseModel):
    """ Model for report presence resolution result. """

    exists: bool
    s3_enabled: bool = False
    report_status: Optional[TestReportStatus]

    @property
    def not_ready(self) -> bool:
        return self.s3_enabled and not self.exists and self.report_status is TestReportStatus.GENERATED
