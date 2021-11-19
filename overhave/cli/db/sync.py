import click


def _git_sync() -> None:
    pass


@click.command(short_help="Synchronize features with actual state of git repository on default branch")
@click.pass_obj
def git_sync() -> None:
    """Create all metadata tables."""
    _git_sync()
