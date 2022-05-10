import logging
import re

from flask_login import current_user
from wtforms import Form, ValidationError

from overhave import db
from overhave.admin.views.base import ModelViewConfigured

logger = logging.getLogger(__name__)


class TagsView(ModelViewConfigured):
    """View for :class:`Tags` table."""

    can_view_details = False

    column_list = ("value", "created_at", "created_by")
    form_excluded_columns = ("created_at",)
    column_searchable_list = ("value", "created_by")
    column_filters = ("value", "created_by")

    _tag_name_pattern = re.compile(r"^[0-9a-zA-Zа-яА-ЯёЁ_]+$")

    def on_model_change(self, form: Form, model: db.Tags, is_created: bool) -> None:
        tag = form.data.get("value")
        if tag is not None and not self._tag_name_pattern.match(tag):
            raise ValidationError("Unsupported symbols in tag name!")
        if not is_created:
            if current_user.login == model.created_by or current_user.role == db.Role.admin:
                return
            raise ValidationError("Only tag creator or administrator could edit it!")
        model.created_by = current_user.login

    def on_model_delete(self, model: db.Tags) -> None:
        if not (current_user.login == model.created_by or current_user.role == db.Role.admin):
            raise ValidationError("Only author or administrator could delete tags!")
