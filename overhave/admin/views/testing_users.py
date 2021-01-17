from typing import Dict, Optional, Type, Union

from flask_admin.form import JSONField
from flask_login import current_user
from pydantic import BaseModel
from wtforms import Form, ValidationError

from overhave import db
from overhave.admin.views.base import ModelViewConfigured
from overhave.admin.views.formatters import json_formatter
from overhave.factory import proxy_factory


def _make_dict_from_model(model: Optional[Type[BaseModel]]) -> Optional[Dict[str, Union[int, str]]]:
    if model is not None:
        prepared_dict = {}
        for key, value in model.__fields__.items():
            prepared_dict[key] = value.type_.__name__
        return prepared_dict
    return None


class TestingUserView(ModelViewConfigured):
    """ View for :class:`TestUser` table. """

    create_template = 'test_user_create.html'
    edit_template = 'test_user_edit.html'

    can_view_details = False
    column_list = ['id', 'name', 'feature_type', 'specification', 'created_by']
    column_searchable_list = ['name', 'created_by']
    form_excluded_columns = ('created_at', 'creator')
    form_overrides = dict(specification=JSONField)

    form_extra_fields = {'template': JSONField('Specification format')}
    form_widget_args = {'template': {'readonly': True}}

    column_formatters = dict(specification=json_formatter,)

    column_descriptions = dict(
        name="Test user name",
        feature_type="Type of scenarios set, where test user will be used",
        specification="Test user specification in JSON format placed below",
    )

    _feature_type: Optional[str] = None

    def on_form_prefill(self, form, id) -> None:  # type: ignore  # noqa: A002
        if isinstance(form._obj, db.TestUser):
            self._feature_type = form._obj.feature_type.name

    def get_specification_template(self) -> Optional[Dict[str, Union[int, str]]]:
        if self._feature_type is None:
            self._feature_type = proxy_factory.feature_type_storage.get_default_feature_type().name
        parser = proxy_factory.context.project_settings.user_spec_template_mapping.get(self._feature_type)
        return _make_dict_from_model(parser)

    @staticmethod
    def _validate_json(model: db.TestUser) -> None:
        if not isinstance(model.specification, dict):
            raise ValidationError('Could not convert specified data into correct JSON!')
        parser = proxy_factory.context.project_settings.user_spec_template_mapping.get(model.feature_type.name)
        if parser is not None:
            try:
                parser.parse_obj(model.specification)
            except ValueError:
                raise ValidationError(f'Could not convert specified data into {parser.__name__} model!')

    def on_model_change(self, form: Form, model: db.TestUser, is_created: bool) -> None:
        self._feature_type = model.feature_type.name
        self._validate_json(model)
        if is_created:
            model.created_by = current_user.login

    def on_model_delete(self, model: db.TestUser) -> None:
        if not (current_user.login == model.created_by or current_user.role == db.Role.admin):
            raise ValidationError('Only test user creator or administrator could delete test user!')
