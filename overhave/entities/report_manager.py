import logging
import subprocess
from os import makedirs
from pathlib import Path
from typing import Optional
from uuid import uuid1

from overhave.db import TestReportStatus
from overhave.entities.archiver import ArchiveManager
from overhave.entities.settings import OverhaveFileSettings, OverhaveReportManagerSettings
from overhave.storage import set_report
from overhave.transport import OverhaveS3Bucket, S3Manager

logger = logging.getLogger(__name__)


class ReportManager:
    """ Class for Allure reports creation and management. """

    def __init__(
        self,
        settings: OverhaveReportManagerSettings,
        file_settings: OverhaveFileSettings,
        archive_manager: ArchiveManager,
        s3_manager: S3Manager,
    ) -> None:
        self._settings = settings
        self._file_settings = file_settings
        self._archive_manager = archive_manager
        self._s3_manager = s3_manager

    def _generate_report(self, alluredir: Path, report_dir: Path) -> Optional[int]:
        generation_cmd = [
            self._settings.allure_cmdline,
            "generate",
            f"{alluredir}/",
            "--output",
            report_dir.as_posix(),
            "--clean",
        ]
        logger.debug("Allure report generation command: %s", " ".join(generation_cmd))
        makedirs(report_dir.as_posix(), exist_ok=True)
        try:
            return subprocess.run(
                generation_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self._settings.report_creation_timeout,
                check=True,
            ).returncode
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.exception("Error while generating Allure report!")
            return None

    def _process_generated_report(self, test_run_id: int, report_dir: Path) -> None:
        set_report(run_id=test_run_id, status=TestReportStatus.GENERATED, report=report_dir.name)
        zip_report = self._archive_manager.zip_path(report_dir)
        logger.info("Zip Allure report: %s", zip_report)
        if not self._s3_manager.enabled:
            return
        upload_result = self._s3_manager.upload_file(file=zip_report, bucket=OverhaveS3Bucket.REPORTS)
        if not upload_result:
            return
        set_report(run_id=test_run_id, status=TestReportStatus.SAVED)

    def create_allure_report(self, test_run_id: int, results_dir: Path) -> None:
        report_dir = self._file_settings.tmp_reports_dir / uuid1().hex
        logger.debug("Allure report directory: %s", report_dir)

        report_generation_returncode = self._generate_report(alluredir=results_dir, report_dir=report_dir)
        if report_generation_returncode != 0:
            set_report(run_id=test_run_id, status=TestReportStatus.GENERATION_FAILED)
            return
        logger.debug("Allure report successfully generated to directory: %s", report_dir.as_posix())
        self._process_generated_report(test_run_id=test_run_id, report_dir=report_dir)
