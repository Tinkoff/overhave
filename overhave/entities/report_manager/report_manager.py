import logging
import subprocess  # noqa: S404
from os import makedirs
from pathlib import Path
from typing import Optional
from uuid import uuid1

from overhave.db import TestReportStatus
from overhave.entities.archiver import ArchiveManager
from overhave.entities.report_manager.models import ReportPresenceResolution
from overhave.entities.settings import OverhaveFileSettings, OverhaveReportManagerSettings
from overhave.storage import ITestRunStorage
from overhave.transport import OverhaveS3Bucket, S3Manager

logger = logging.getLogger(__name__)


class ReportManager:
    """Class for Allure reports creation and management."""

    def __init__(
        self,
        settings: OverhaveReportManagerSettings,
        file_settings: OverhaveFileSettings,
        test_run_storage: ITestRunStorage,
        archive_manager: ArchiveManager,
        s3_manager: S3Manager,
    ) -> None:
        self._settings = settings
        self._file_settings = file_settings
        self._test_run_storage = test_run_storage
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
            return subprocess.run(  # noqa: S603
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
        self._test_run_storage.set_report(run_id=test_run_id, status=TestReportStatus.GENERATED, report=report_dir.name)
        if not self._s3_manager.enabled:
            return
        zip_report = self._archive_manager.archive_path(path=report_dir, extension=self._settings.archive_extension)
        logger.info("Zip Allure report: %s", zip_report)
        upload_result = self._s3_manager.upload_file(file=zip_report, bucket=OverhaveS3Bucket.REPORTS)
        if not upload_result:
            return
        self._test_run_storage.set_report(run_id=test_run_id, status=TestReportStatus.SAVED)
        zip_report.unlink()

    def create_allure_report(self, test_run_id: int, results_dir: Path) -> None:
        report_dir = self._file_settings.tmp_reports_dir / uuid1().hex
        logger.debug("Allure report directory: %s", report_dir)

        report_generation_returncode = self._generate_report(alluredir=results_dir, report_dir=report_dir)
        if report_generation_returncode != 0:
            self._test_run_storage.set_report(run_id=test_run_id, status=TestReportStatus.GENERATION_FAILED)
            return
        logger.debug("Allure report successfully generated to directory: %s", report_dir.as_posix())
        self._process_generated_report(test_run_id=test_run_id, report_dir=report_dir)

    def get_report_precense_resolution(self, report: str, run_id: int) -> ReportPresenceResolution:  # noqa: C901
        report_index = Path(self._file_settings.tmp_reports_dir / report)
        report_dir = report_index.parent
        if report_dir.exists() and report_index.exists():
            return ReportPresenceResolution(exists=True)

        if not report_dir.exists():
            logger.warning("Report '%s' does not exist!", report_index.parent.name)
        if not report_index.exists():
            logger.warning("Report '%s' does not contain compiled files for HTML view!", report_index.parent.name)
        test_run = self._test_run_storage.get_test_run(run_id)
        if test_run is None:
            logger.warning("No one test run with id=%s exists!", run_id)
            return ReportPresenceResolution(exists=False)

        resolution = ReportPresenceResolution(
            exists=False, s3_enabled=self._s3_manager.enabled, report_status=test_run.report_status
        )
        if not test_run.report_status.has_report:
            logger.warning("TestRun with id=%s has not got report!", run_id)
            return resolution
        if not self._s3_manager.enabled:
            logger.info("S3Manager disabled, so could not download file from s3 cloud.")
            return resolution
        if test_run.report_status is TestReportStatus.GENERATED:
            logger.warning(
                "File %s after TestRun with id=%s has been generated, but still not uploaded!", test_run.report, run_id
            )
            return resolution
        zip_report_path = self._file_settings.tmp_reports_dir / (
            report_dir.name + f".{self._settings.archive_extension}"
        )
        zip_report_path.parent.mkdir(parents=True, exist_ok=True)
        download_success = self._s3_manager.download_file(
            filename=zip_report_path.name, dir_to_save=zip_report_path.parent, bucket=OverhaveS3Bucket.REPORTS.value
        )
        if not download_success:
            logger.error("Report archive '%s' is not available on s3 cloud!", zip_report_path.name)
            return resolution

        unpacked_report = self._archive_manager.unpack_path(
            path=zip_report_path, extension=self._settings.archive_extension
        )
        zip_report_path.unlink()
        logger.info("Unpacked Allure report: %s", unpacked_report)
        resolution.exists = True
        return resolution
