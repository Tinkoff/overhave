import logging
import subprocess
import tempfile
import uuid
from functools import cached_property
from http import HTTPStatus
from multiprocessing.pool import ThreadPool
from os import makedirs
from pathlib import Path
from typing import Optional

import flask
import werkzeug

from overhave import db
from overhave.entities.archiver import ArchiveManager
from overhave.entities.converters import ProcessingContext, get_context_by_test_run_id
from overhave.entities.settings import OverhaveFileSettings, ProcessorSettings
from overhave.entities.stash import IStashProjectManager
from overhave.processing.abstract import IProcessor
from overhave.scenario import FileManager
from overhave.storage import save_draft, set_report, set_run_status, set_traceback
from overhave.storage.version import UniqueDraftCreationError, add_pr_url
from overhave.testing import ConfigInjector, PytestRunner
from overhave.transport import OverhaveS3Bucket, S3Manager

logger = logging.getLogger(__name__)


class Processor(IProcessor):
    """ Class for application entity tasks processing in instance of :class:`ThreadPool`. """

    def __init__(
        self,
        settings: ProcessorSettings,
        file_settings: OverhaveFileSettings,
        injector: ConfigInjector,
        file_manager: FileManager,
        test_runner: PytestRunner,
        stash_manager: IStashProjectManager,
        archive_manager: ArchiveManager,
        s3_manager: S3Manager,
    ):
        self._settings = settings
        self._file_settings = file_settings
        self._injector = injector
        self._file_manager = file_manager
        self._test_runner = test_runner
        self._stash_manager = stash_manager
        self._archive_manager = archive_manager
        self._s3_manager = s3_manager

    @cached_property
    def _thread_pool(self) -> ThreadPool:
        return ThreadPool(processes=self._settings.processes_num)

    def _run_test(self, context: ProcessingContext, alluredir: Path) -> int:
        with self._file_manager.tmp_feature_file(context=context) as feature_file:
            with self._file_manager.tmp_fixture_file(context=context, feature_file=feature_file) as fixture_file:
                return self._test_runner.run(fixture_file=fixture_file.name, alluredir=alluredir.as_posix(),)

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

    def _process_generated_report(self, run_id: int, report_dir: Path) -> None:
        set_report(run_id=run_id, status=db.TestReportStatus.GENERATED, report=f"{report_dir.name}/index.html")
        zip_report = self._archive_manager.zip_path(report_dir)
        logger.info("Zip Allure report: %s", zip_report)
        if not self._s3_manager.enabled:
            return
        self._s3_manager.upload_file(file=zip_report, bucket=OverhaveS3Bucket.REPORTS)
        set_report(run_id=run_id, status=db.TestReportStatus.SAVED)

    def _process_run(self, run_id: int) -> None:
        set_run_status(run_id=run_id, status=db.TestRunStatus.RUNNING)
        try:
            ctx = get_context_by_test_run_id(run_id)

            allure_dir = Path(tempfile.mkdtemp())
            logger.debug("Allure results directory path: %s", allure_dir.as_posix())

            test_return_code = self._run_test(context=ctx, alluredir=allure_dir)
            logger.debug("Test returncode: %s", test_return_code)

            if test_return_code == 0:
                set_run_status(run_id=run_id, status=db.TestRunStatus.SUCCESS)
            else:
                set_traceback(run_id, "Test run failed! Something went wrong...")
                set_run_status(run_id=run_id, status=db.TestRunStatus.FAILED)

            allure_tmpdir_name = str(uuid.uuid1())
            logger.debug("Allure report directory: %s", allure_tmpdir_name)
            report_dir = self._file_settings.tmp_reports_dir / allure_tmpdir_name

            report_generation_returncode = self._generate_report(alluredir=allure_dir, report_dir=report_dir)
            if report_generation_returncode != 0:
                set_report(run_id=run_id, status=db.TestReportStatus.GENERATION_FAILED)
                return
            logger.debug("Allure report successfully generated to directory: %s", report_dir.as_posix())
            self._process_generated_report(run_id=run_id, report_dir=report_dir)

        except Exception as e:
            logger.exception("Error!")
            set_run_status(run_id, db.TestRunStatus.INTERNAL_ERROR)
            set_traceback(run_id, f"{e}")

    def execute_test(self, test_run_id: int) -> werkzeug.Response:
        self._thread_pool.apply_async(self._process_run, args=(test_run_id,))
        logger.debug("Redirect to TestRun details view with test_run_id %s", test_run_id)
        return flask.redirect(flask.url_for("testrun.details_view", id=test_run_id))

    def _create_version(self, test_run_id: int, draft_id: int) -> None:
        try:
            response = self._stash_manager.create_pull_request(test_run_id)
            logger.info("Stash PR response has been gotten")
            add_pr_url(draft_id=draft_id, response=response)
            logger.info("Stash PR result has been written")
        except Exception:
            logger.exception("Error while trying to create Stash PR!")

    def create_version(self, test_run_id: int, published_by: str) -> werkzeug.Response:
        try:
            draft_id = save_draft(test_run_id=test_run_id, published_by=published_by)
        except UniqueDraftCreationError:
            error_msg = "Error while creation draft!"
            logger.exception(error_msg)
            flask.flash(error_msg, category="error")
            return flask.redirect(
                flask.url_for("testrun.details_view", id=test_run_id), code=HTTPStatus.UNPROCESSABLE_ENTITY
            )
        self._thread_pool.apply_async(self._create_version, args=(test_run_id, draft_id))
        return flask.redirect(flask.url_for("draft.details_view", id=draft_id))
