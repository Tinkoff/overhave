import typer

from overhave.base_settings import DataBaseSettings
from overhave.cli.db_cmds.regular import create_schema, drop_schema, set_config_to_context


def _config_callback(ctx: typer.Context) -> None:
    set_config_to_context(context=ctx, settings=DataBaseSettings())


db_app = typer.Typer(short_help="Commands for simple database operations", callback=_config_callback)


@db_app.command(short_help="Create all metadata tables")
def create_all(ctx: typer.Context) -> None:
    """Create all metadata tables."""
    create_schema(config=ctx.obj)


@db_app.command(short_help="Drop all metadata tables, attributes, schema")
def drop_all(ctx: typer.Context) -> None:
    """Drop all metadata tables, attributes, schema."""
    typer.confirm("Does it really need?", abort=True)
    drop_schema(config=ctx.obj)
