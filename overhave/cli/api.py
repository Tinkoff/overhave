import typer
import uvicorn

from overhave.cli.group import overhave


@overhave.command(short_help="Run Overhave API")
def api(
    port: int = typer.Option(8000, "-p", "--port", help="Service port"),
    workers: int = typer.Option(1, "-w", "--workers", help="Uvicorn workers"),
) -> None:
    """Run Overhave API."""
    from overhave.api.asgi import app
    from overhave.api.settings import OverhaveUvicornApiSettings

    settings = OverhaveUvicornApiSettings(port=port, workers=workers)
    uvicorn.run(app, **settings.dict())
