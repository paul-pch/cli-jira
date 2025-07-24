import unittest

from typer.testing import CliRunner

from app.main import app

runner = CliRunner()


class TestMain(unittest.TestCase):
    def test_hello_command(self) -> None:
        """Test the hello command with default name."""
        with self.assertLogs("app.main", level="INFO") as log:
            result = runner.invoke(app, ["--name", "World"])
            assert result.exit_code == 0
            assert "Hello World! Welcome to your Python CLI application." in log.output[0]

    def test_hello_with_name(self) -> None:
        """Test the hello command with a specific name."""
        with self.assertLogs("app.main", level="INFO") as log:
            result = runner.invoke(app, ["--name", "Alice"])
            assert result.exit_code == 0
            assert "Hello Alice! Welcome to your Python CLI application." in log.output[0]
