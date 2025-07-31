from typer.testing import CliRunner

from app.project import app

runner = CliRunner()


def test_app():
    result = runner.invoke(
        app,
    )  # Normalement y a l'argument list mais là non car on a qu'une méthode dans la classe source je suppose
    print("STDOUT:\n", result.output)
    print("STDERR:\n", result.stderr)
    assert result.exit_code == 0
    assert "Available Jira Projects" in result.output
