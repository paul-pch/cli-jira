from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_app() -> None:
    result = runner.invoke(app, ["list", "project"])
    assert result.exit_code == 0
    assert "ST" in result.output
    assert "Socle Technique" in result.output
