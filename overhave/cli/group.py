import typer as typer

from overhave.cli.db_cmds import db_app
from overhave.cli.s3 import s3_app

overhave: typer.Typer = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
overhave.add_typer(db_app, name="db")
overhave.add_typer(s3_app, name="s3")
