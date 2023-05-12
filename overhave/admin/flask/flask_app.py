from flask import Flask


def get_flask_app(template_folder: str) -> Flask:
    app = Flask("admin", template_folder=template_folder)
    app.secret_key = "overhave cool secret key"
    app.config.update({"FLASK_ADMIN_SWATCH": "united", "FLASK_ADMIN_FLUID_LAYOUT": True})
    return app
