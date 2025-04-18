import click.testing as CliRunner

from src.fetch_take_home_sre import cli

def test_cli(sample_yaml):
    runner = CliRunner.CliRunner()
    result = runner.invoke(cli.monitor, [sample_yaml.as_posix(), "-r", "1", "-f", "2"])
    print(result)
    assert result.exit_code == 0
    assert "Run complete!" in result.output
    assert "Health:" in result.output