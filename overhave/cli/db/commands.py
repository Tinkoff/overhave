import click

from overhave.base_settings import DataBaseSettings
from overhave.cli.db.regular import create_all, drop_all, set_config_to_context
from overhave.cli.group import overhave


def _db_commands(group: click.Group) -> click.Group:
    """ Add commands to group. """
    group.add_command(create_all)
    group.add_command(drop_all)
    return group


@_db_commands
@overhave.group(short_help='Commands for simple database operations')
@click.pass_context
def db(ctx: click.Context) -> None:
    """ Commands for simple database operations. """
    set_config_to_context(context=ctx, settings=DataBaseSettings())
