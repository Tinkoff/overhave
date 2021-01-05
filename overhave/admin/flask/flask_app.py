import jinja2
from flask import Flask


def get_flask_app(template_folder: str) -> Flask:
    app = Flask('admin', template_folder=template_folder)
    app.secret_key = 'overhave cool secret key'
    app.config.update({'FLASK_ADMIN_SWATCH': 'united', 'FLASK_ADMIN_FLUID_LAYOUT': True})

    login_template_loader = jinja2.FileSystemLoader([template_folder])
    app.jinja_loader = jinja2.ChoiceLoader([app.jinja_loader, login_template_loader])  # type: ignore
    return app
