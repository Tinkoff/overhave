import json
import logging
import re
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional

import flask
import werkzeug
from flask_admin import expose
from flask_admin.model import InlineFormAdmin
from flask_login import current_user
from markupsafe import Markup
from wtforms import Field, TextAreaField, ValidationError
from wtforms.widgets import HiddenInput

from overhave import db
from overhave.admin.views.base import ModelViewConfigured
from overhave.factory import get_admin_factory, get_test_execution_factory
from overhave.transport import TestRunData, TestRunTask

logger = logging.getLogger(__name__)

_SCENARIO_PREFIX = "scenario-0"


class ScenarioTextWidget(HiddenInput):
    """ Widget to override scenario view. """

    def __call__(self, field: Field, **kwargs: Any) -> Any:
        widget_name = type(self).__name__
        logger.debug("%s field id: '%s'", widget_name, field.id)
        inputs = super().__call__(field, **kwargs)
        logger.debug("%s inputs: '%s'", widget_name, inputs)
        return inputs + Markup(f'<div class="editor" ref="{field.id}" id="{field.id}-editor"></div>')


class ScenarioTextAreaField(TextAreaField):
    """ Field to override scenario view. """

    widget = ScenarioTextWidget()


class ScenarioInlineModelForm(InlineFormAdmin):
    """ Form to override scenario view. """

    form_overrides = dict(text=ScenarioTextAreaField)
    form_excluded_columns = ("created_at", "test_runs")


class FeatureView(ModelViewConfigured):
    """ View for :class:`Feature` table. """

    can_view_details = False

    inline_models = (ScenarioInlineModelForm(db.Scenario),)

    create_template = "feature_create.html"
    edit_template = "feature_edit.html"

    column_list = (
        "id",
        "name",
        "feature_type",
        "file_path",
        "feature_tags",
        "task",
        "author",
        "created_at",
        "last_edited_by",
        "released",
    )
    form_excluded_columns = (
        "created_at",
        "last_edited_by",
        "released",
        "versions",
        "feature_tags.value",
    )

    column_searchable_list = [
        "id",
        "name",
        "task",
        "author",
        "file_path",
        "last_edited_by",
        "feature_tags.value",
    ]
    column_filters = ("name", "feature_type", "last_edited_by", "author", "created_at", "feature_tags.value")
    column_sortable_list = ("id", "name", "author", "last_edited_by")
    column_labels = {
        "file_path": "File",
        "feature_tags": "Tags",
        "feature_type": "Type",
        "name": "Name",
        "task": "Tasks",
    }

    _task_pattern = re.compile(r"\w+[-]\d+")
    _file_path_pattern = re.compile(r"^[0-9a-zA-Zа-яА-ЯёЁ_/\\ ]{8,}")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def _validate_tasks(cls, tasks: List[str]) -> None:
        for task in tasks:
            if cls._task_pattern.match(task):
                continue
            raise ValidationError(
                f"Incorrect format of task specification: '{task}'! "
                "Supported: <PROJECT>-<NUMBER>, for example 'PRJ-1234'."
            )

    @classmethod
    def _make_file_path(cls, file_path: str) -> str:
        feature_suffix = get_admin_factory().context.file_settings.feature_suffix
        if file_path.rstrip().endswith(feature_suffix):
            file_path = file_path.removesuffix(feature_suffix)
        if not cls._file_path_pattern.match(file_path):
            raise ValidationError(
                f"Incorrect format of file path specification: '{file_path}'! "
                f"Supported pattern: {cls._file_path_pattern.pattern}, for example 'my_folder / my_filename(.feature)'."
                " At least 8 characters long."
            )
        path = Path(file_path.replace(" ", "")).with_suffix(feature_suffix).as_posix()
        logger.debug("Processed feature file path: '%s'", path)
        return path

    def on_model_change(self, form, model: db.Feature, is_created) -> None:  # type: ignore
        self._validate_tasks(model.task)
        model.file_path = self._make_file_path(model.file_path)
        if is_created:
            model.author = current_user.login
        model.last_edited_by = current_user.login
        model.released = False

    def on_model_delete(self, model) -> None:  # type: ignore
        if not (current_user.login == model.author or current_user.role == db.Role.admin):
            raise ValidationError("Only feature author or administrator could delete feature!")

    @cached_property
    def get_bdd_steps(self) -> Dict[str, Dict[str, List[str]]]:
        factory = get_admin_factory()
        return {
            feature_type: factory.step_collector.get_steps(feature_type)
            for feature_type in factory.feature_extractor.feature_types
        }

    @property
    def browse_url(self) -> Optional[str]:
        browse_url_value = get_admin_factory().context.project_settings.browse_url
        if browse_url_value is not None:
            return browse_url_value.human_repr()
        return None

    @property
    def feature_suffix(self) -> str:
        return get_admin_factory().context.file_settings.feature_suffix

    @staticmethod
    def _run_test(data: Dict[str, Any], rendered: werkzeug.Response) -> werkzeug.Response:
        scenario_id = data.get(f"{_SCENARIO_PREFIX}-id")
        scenario_text = data.get(f"{_SCENARIO_PREFIX}-text")
        if not scenario_id or not scenario_text:
            flask.flash("Scenario information not requested.", category="error")
            return rendered
        factory = get_admin_factory()
        scenario = factory.scenario_storage.get_scenario(int(scenario_id))
        if scenario is None:
            flask.flash("Scenario does not exist, so could not run test.", category="error")
            return rendered
        test_run_id = factory.test_run_storage.create_test_run(scenario_id=scenario.id, executed_by=current_user.login)
        if not factory.context.admin_settings.consumer_based:
            factory.threadpool.apply_async(get_test_execution_factory().test_executor.execute_test, args=(test_run_id,))
        if factory.context.admin_settings.consumer_based and not factory.redis_producer.add_task(
            TestRunTask(data=TestRunData(test_run_id=test_run_id))
        ):
            flask.flash("Problems with Redis service! TestRunTask has not been sent.", category="error")
            return rendered
        logger.debug("Redirect to TestRun details view with test_run_id='%s'...", test_run_id)
        return flask.redirect(flask.url_for("testrun.details_view", id=test_run_id))

    @expose("/edit/", methods=("GET", "POST"))
    def edit_view(self) -> werkzeug.Response:
        rendered: werkzeug.Response = super().edit_view()
        if flask.request.method != "POST":
            return rendered

        data = flask.request.form
        logger.debug("Request data:\n%s", json.dumps(data))
        run_scenario_action = data.get("run")
        if not run_scenario_action:
            logger.debug("Show rendered EditView")
            return rendered

        logger.debug("Process feature 'RUN' request")
        tasks = data["task"].split(",")
        self._validate_tasks(tasks=tasks)

        mutable_data = dict(data)
        mutable_data["file_path"] = self._make_file_path(data["file_path"])

        return self._run_test(data, rendered)
