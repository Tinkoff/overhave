import typer

from overhave.cli.db_cmds.regular import create_schema, drop_schema


class TestOverhaveDatabaseCmds:
    """Sanity tests for database operating CLI commands."""

    def test_create_all(self, typer_ctx_mock: typer.Context, set_config_to_ctx: None) -> None:
        create_schema(typer_ctx_mock.obj)

    def test_drop_all(self, typer_ctx_mock: typer.Context, set_config_to_ctx: None) -> None:
        drop_schema(typer_ctx_mock.obj)
