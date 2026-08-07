import pytest
from click.shell_completion import ShellComplete
from typer.main import get_command

from main import app


def complete(args: list[str], incomplete: str = "") -> list[str]:
    completion = ShellComplete(get_command(app), {}, "jira", "_JIRA_COMPLETE")

    return [item.value for item in completion.get_completions(args, incomplete)]


class TestShellCompletion:
    @staticmethod
    def test_top_level_commands() -> None:
        assert set(complete([])) >= {"create", "get", "edit", "delete"}

    @staticmethod
    def test_subcommands() -> None:
        assert "issues" in complete(["get"])

    @staticmethod
    def test_options_of_a_subcommand() -> None:
        assert "--worklog" in complete(["edit", "issue", "ST-1"], "--work")

    @staticmethod
    def test_works_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
        """Completion must not run the callback: it would demand env vars and open a connection."""
        for name in ("JIRA_URL", "JIRA_EMAIL", "JIRA_TOKEN"):
            monkeypatch.delenv(name, raising=False)

        assert "issues" in complete(["get"])
