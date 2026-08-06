from pathlib import Path

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


def test_incomplete_config_file_prints_friendly_warning(
    jira_env: None,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An incomplete config.toml used to crash with a raw KeyError inside the command."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('[default]\nproject = "ST"\n', encoding="utf-8")
    monkeypatch.setattr("app.utils.utils.find_config", lambda: str(config_file))

    result = runner.invoke(app, ["get", "projects"])

    assert result.exit_code == 1
    assert "configuration invalide" in result.output
    assert "issue_type" in result.output
