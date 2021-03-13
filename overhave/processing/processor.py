import logging
import tempfile
from functools import cached_property
from http import HTTPStatus
from multiprocessing.pool import ThreadPool
from pathlib import Path

import flask
import werkzeug

from overhave.db import TestRunStatus
from overhave.entities.converters import ProcessingContext, get_context_by_test_run_id
from overhave.entities.report_manager import ReportManager
from overhave.entities.settings import OverhaveFileSettings, ProcessorSettings
from overhave.entities.stash import IStashProjectManager
from overhave.processing.abstract import IProcessor
from overhave.scenario import FileManager
from overhave.storage import ITestRunStorage, UniqueDraftCreationError, add_pr_url, save_draft
from overhave.testing import ConfigInjector, PytestRunner

logger = logging.getLogger(__name__)


class Processor(IProcessor):
    """ Class for application entity tasks processing in instance of :class:`ThreadPool`. """

    def __init__(
        self,
        settings: ProcessorSettings,
        file_settings: OverhaveFileSettings,
        test_run_storage: ITestRunStorage,
        injector: ConfigInjector,
        file_manager: FileManager,
        test_runner: PytestRunner,
        stash_manager: IStashProjectManager,
        report_manager: ReportManager,
    ):
        self._settings = settings
        self._file_settings = file_settings
        self._test_run_storage = test_run_storage
        self._injector = injector
        self._file_manager = file_manager
        self._test_runner = test_runner
        self._stash_manager = stash_manager
        self._report_manager = report_manager

    @cached_property
    def _thread_pool(self) -> ThreadPool:
        return ThreadPool(processes=self._settings.processes_num)

    def _run_test(self, context: ProcessingContext, alluredir: Path) -> int:
        with self._file_manager.tmp_feature_file(context=context) as feature_file:
            with self._file_manager.tmp_fixture_file(context=context, feature_file=feature_file) as fixture_file:
                return self._test_runner.run(fixture_file=fixture_file.name, alluredir=alluredir.as_posix())

    def _process_run(self, run_id: int) -> None:
        self._test_run_storage.set_run_status(run_id=run_id, status=TestRunStatus.RUNNING)
        ctx = get_context_by_test_run_id(run_id)
        results_dir = Path(tempfile.mkdtemp())
        logger.debug("Allure results directory path: %s", results_dir.as_posix())
        try:
            test_return_code = self._run_test(context=ctx, alluredir=results_dir)
        except Exception as e:
            logger.exception("Error!")
            self._test_run_storage.set_run_status(run_id=run_id, status=TestRunStatus.INTERNAL_ERROR, traceback=str(e))
            return

        logger.debug("Test returncode: %s", test_return_code)
        if test_return_code == 0:
            self._test_run_storage.set_run_status(run_id=run_id, status=TestRunStatus.SUCCESS)
        else:
            self._test_run_storage.set_run_status(
                run_id=run_id, status=TestRunStatus.FAILED, traceback="Test run failed!"
            )
        self._report_manager.create_allure_report(test_run_id=run_id, results_dir=results_dir)

    def execute_test(self, scenario_id: int, executed_by: str) -> werkzeug.Response:
        test_run_id = self._test_run_storage.create_test_run(scenario_id=scenario_id, executed_by=executed_by)
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
