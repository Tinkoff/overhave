import click

from overhave.cli.db.regular import _create_all, _drop_all


class TestOverhaveDatabaseCmds:
    """ Sanity tests for database operating CLI commands. """

    def test_create_all(self, click_ctx_mock: click.Context, set_config_to_ctx: None):
        _create_all(click_ctx_mock.obj)

    def test_drop_all(self, click_ctx_mock: click.Context, set_config_to_ctx: None):
        _drop_all(click_ctx_mock.obj)
