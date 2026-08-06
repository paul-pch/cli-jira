import pytest

from main import app
from tests.conftest import runner


def test_missing_env_vars_prints_friendly_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing env var used to crash with a raw traceback instead of a readable message."""
    monkeypatch.delenv("JIRA_URL", raising=False)
    monkeypatch.delenv("JIRA_EMAIL", raising=False)
    monkeypatch.delenv("JIRA_TOKEN", raising=False)

    result = runner.invoke(app, ["get", "projects"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "JIRA_URL" in result.output
    assert "JIRA_EMAIL" in result.output
    assert "JIRA_TOKEN" in result.output
