from overhave.api.app import create_overhave_api
from overhave.base_settings import DataBaseSettings, LoggingSettings

DataBaseSettings().setup_db()
LoggingSettings().setup_logging()

app = create_overhave_api()
