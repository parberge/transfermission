from click.testing import CliRunner
from cli import cli


def test_cli():
    runner = CliRunner()
    # Just a rudimentary (smoke test) of the CLI
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
