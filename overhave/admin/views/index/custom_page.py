import typing
from pathlib import Path

from flask_admin.form import BaseForm
from flask_admin.model.widgets import XEditableWidget
from markupsafe import Markup
from wtforms import Field


class CustomPageWidget(XEditableWidget):
    """ Customising widget.

    Widget content is filled with content from specified
    ``self.template_path```.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.template_path: typing.Optional[Path] = None
        super().__init__(*args, **kwargs)

    def __call__(self, field: Field, **kwargs: typing.Any) -> Markup:
        if self.template_path is not None:
            with self.template_path.open('r') as template:
                return Markup(template.read())
        return Markup("This is Overhave info page.")


class CustomPageField(Field):
    """ Field for custom page widget. """

    widget = CustomPageWidget()


class CustomPageForm(BaseForm):
    """ Form for custom page. """

    type = CustomPageField()

    def __init__(self, template_path: typing.Optional[Path]):
        super().__init__()
        self.type.widget.template_path = template_path
        self.type.label = None
