import logging

from flask_login import current_user
from overhave import db
from overhave.admin.views.base import ModelViewConfigured
from overhave.admin.views.feature import ScenarioInlineModelForm

logger = logging.getLogger(__name__)


class TagsView(ModelViewConfigured):
    """ View for :class:`Feature` table. """

    can_view_details = False

    # inline_models = (ScenarioInlineModelForm(db.Feature),)
    # create_template = "tag.html"
    # edit_template = ".html"

    column_list = (
        "id",
        "tags",
        "created_at",
        "feature_id",
        "created_by",
    )

    def on_model_change(self, form, model: db.FeatureTags, is_created) -> None:  # type: ignore
        model.created_by = current_user.login

