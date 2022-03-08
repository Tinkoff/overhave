from overhave import OverhaveAdminApp, overhave_app
from overhave.base_settings import DataBaseSettings, LoggingSettings
from overhave.cli.group import overhave
from overhave.factory import get_admin_factory


def _get_admin_app() -> OverhaveAdminApp:
    DataBaseSettings().setup_db()
    LoggingSettings().setup_logging()
    return overhave_app(get_admin_factory())


@overhave.command(short_help="Run Overhave Admin panel")
def admin(port: int = 8076, debug: bool = False) -> None:
    _get_admin_app().run(host="localhost", port=port, debug=debug)
