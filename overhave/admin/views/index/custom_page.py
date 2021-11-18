import typing
from pathlib import Path

from flask_admin.form import BaseForm
from flask_admin.model.widgets import XEditableWidget
from markupsafe import Markup
from wtforms import Field


class CustomPageWidget(XEditableWidget):
    """Customising widget.

    Widget content is filled with content from specified
    ``self.template_path```.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.template_path: typing.Optional[Path] = None
        super().__init__(*args, **kwargs)

    def __call__(self, field: Field, **kwargs: typing.Any) -> Markup:
        if self.template_path is not None:
            with self.template_path.open("r") as template:
                return Markup(template.read())
        return Markup(
            """
            <h1>Overhave index</h1>
            <p>This is Overhave info page. You could replace this page with your own HTML template.</p>
            <p>It is possible via <a href="https://overhave.readthedocs.io/en/latest/#context-setting" target="_blank">
            setting context</a> with <b>OverhaveAdminSettings</b>(index_template_path=<i>&lt;MY_TEMPLATE.html&gt;</i>)
            or through environment variable <b>OVERHAVE_INDEX_TEMPLATE_PATH</b>=<i>&lt;MY_TEMPLATE.html&gt;</i>.
            """
        )


class CustomPageField(Field):
    """Field for custom page widget."""

    widget = CustomPageWidget()


class CustomPageForm(BaseForm):
    """Form for custom page."""

    type = CustomPageField()

    def __init__(self, template_path: typing.Optional[Path]):
        super().__init__()
        self.type.widget.template_path = template_path
        self.type.label = None
