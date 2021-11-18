from flask_login import current_user
from wtforms import ValidationError

from overhave.admin.views.base import ModelViewProtected
from overhave.db import Role


class DraftView(ModelViewProtected):
    """View for :class:`Draft` table."""

    details_template = "draft_detail.html"
    can_delete = True
    column_list = ("id", "feature_id", "test_run_id", "pr_url", "published_by", "created_at", "status")
    column_exclude_list = ("feature", "text")  # type: ignore
    column_details_list = (
        "id",
        "feature_id",
        "test_run_id",
        "pr_url",
        "published_by",
        "created_at",
        "status",
        "traceback",
    )
    column_sortable_list = ("id", "feature_id")
    column_searchable_list = (
        "test_run_id",
        "published_by",
        "pr_url",
    )
    column_filters = ("feature_id", "published_by", "created_at", "status")

    def on_model_delete(self, model) -> None:  # type: ignore
        if not current_user.role == Role.admin:
            raise ValidationError("Only administrator could delete published version of scenario!")
