import logging
import typing
from http import HTTPStatus
from pathlib import Path

import flask
import werkzeug

from overhave import db
from overhave.admin.flask import FlaskLoginManager, get_flask_admin, get_flask_app
from overhave.factory import IAdminFactory, get_publication_factory
from overhave.pytest_plugin import get_proxy_manager
from overhave.storage import UniqueDraftCreationError
from overhave.transport import PublicationData, PublicationTask

logger = logging.getLogger(__name__)

OverhaveAdminApp = typing.NewType("OverhaveAdminApp", flask.Flask)


def _prepare_factory(factory: IAdminFactory) -> None:
    """Resolve necessary settings with :class:`IProxyManager` and prepare :class:`IOverhaveFactory` for usage."""
    proxy_manager = get_proxy_manager()
    proxy_manager.set_factory(factory)
    proxy_manager.patch_pytest()
    proxy_manager.supply_injector_for_collection()
    proxy_manager.injector.collect_configs()


def _resolved_app(factory: IAdminFactory, template_dir: Path) -> flask.Flask:
    """Resolve Flask application with :class:`IOverhaveFactory` and templates directory `template_dir`."""
    flask_app = get_flask_app(template_folder=template_dir.as_posix())
    get_flask_admin(factory).init_app(app=flask_app)
    login_manager = FlaskLoginManager(system_user_storage=factory.system_user_storage, login_view="login")
    login_manager.init_app(flask_app)
    db.ensure_feature_types_exist(factory.feature_extractor.feature_types)  # type: ignore
    return flask_app


def overhave_app(factory: IAdminFactory) -> OverhaveAdminApp:  # noqa: C901
    """Overhave application, based on Flask."""
    current_dir = Path(__file__).parent
    template_dir = current_dir / "templates"
    files_dir = current_dir / "files"

    _prepare_factory(factory)
    flask_app = _resolved_app(factory=factory, template_dir=template_dir)
    flask_app.config["FILES_DIR"] = files_dir

    @flask_app.teardown_request
    def remove_session(exception: typing.Optional[BaseException]) -> None:
        db.current_session.remove()

    @flask_app.route("/reports/<path:request>", methods=["GET", "POST"])
    def get_report(request: str) -> flask.Response:
        if flask.request.method == "POST":
            test_run_id = flask.request.form.get("run_id")
            if test_run_id is None:
                return flask.abort(status=HTTPStatus.BAD_REQUEST)
            report_precense_resolution = factory.report_manager.get_report_precense_resolution(
                report=request, run_id=int(test_run_id)
            )
            if not report_precense_resolution.exists:
                if report_precense_resolution.not_ready:
                    return typing.cast(
                        flask.Response, flask.redirect(f"/reports/{request}", code=HTTPStatus.TEMPORARY_REDIRECT)
                    )
                return flask.abort(status=HTTPStatus.NOT_FOUND)
        return flask.send_from_directory(factory.context.file_settings.tmp_reports_dir, request)

    @flask_app.route("/emulations/<path:url>")
    def go_to_emulation(url: str) -> werkzeug.Response:
        return flask.redirect(factory.context.emulation_settings.get_emulation_url(url))

    @flask_app.route("/pull_request/<int:run_id>")
    def publish_feature(run_id: int) -> werkzeug.Response:
        published_by = flask.request.args.get("published_by")
        if not isinstance(published_by, str):
            flask.flash("Parameter 'published_by' should be specified for version's creation!", category="error")
            return flask.redirect(flask.url_for("testrun.details_view", id=run_id))
        try:
            draft_id = factory.draft_storage.save_draft(
                test_run_id=run_id, published_by=published_by, status=db.DraftStatus.REQUESTED
            )
        except UniqueDraftCreationError:
            logger.exception("Error while creation draft!")
            flask.flash(
                "Requested publication contains scenario which identical to the previous version!", category="warning"
            )
            return flask.redirect(flask.url_for("testrun.details_view", id=run_id))
        if not factory.context.admin_settings.consumer_based:
            factory.threadpool.apply_async(get_publication_factory().publisher.publish_version, args=(draft_id,))
        if factory.context.admin_settings.consumer_based and not factory.redis_producer.add_task(
            PublicationTask(data=PublicationData(draft_id=draft_id))
        ):
            flask.flash("Problems with Redis service! TestRunTask has not been sent.", category="error")
            return flask.redirect(flask.url_for("testrun.details_view", id=run_id))
        return flask.redirect(flask.url_for("draft.details_view", id=draft_id))

    @flask_app.route("/files/<path:file>")
    def get_files(file: str) -> flask.Response:
        return flask.send_from_directory(files_dir, file)

    @flask_app.route("/favicon.ico")
    def favicon() -> flask.Response:
        return flask.send_from_directory(files_dir, "favicon.ico", mimetype="image/vnd.microsoft.icon")

    return OverhaveAdminApp(flask_app)
