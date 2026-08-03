from unittest.mock import MagicMock

from jira import JIRAError

from main import app
from tests.conftest import runner


def test_get_status_catches_jira_error(mock_jira_client: MagicMock) -> None:
    """`get.status` used to have no try/except at all — a real JIRAError crashed the CLI."""
    mock_jira_client.issue.side_effect = JIRAError(status_code=404, text="Issue does not exist")

    result = runner.invoke(app, ["get", "status", "ST-1"])

    assert result.exit_code == 1
    assert "Erreur" in result.output


def test_get_issue_catches_jira_error(mock_jira_client: MagicMock) -> None:
    """JIRAError is what the `jira` lib actually raises, not ConnectionError/TimeoutError/PermissionError."""
    mock_jira_client.issue.side_effect = JIRAError(status_code=401, text="Unauthorized")

    result = runner.invoke(app, ["get", "issue", "ST-1"])

    assert result.exit_code == 1
    assert "Erreur" in result.output


def test_create_issue_catches_jira_error(mock_jira_client: MagicMock) -> None:
    mock_jira_client.create_issue.side_effect = JIRAError(status_code=400, text="Invalid fields")

    result = runner.invoke(app, ["create", "issue", "Titre", "--no-owned"])

    assert result.exit_code == 1
    assert "Erreur" in result.output


def test_edit_issue_catches_jira_error(mock_jira_client: MagicMock) -> None:
    mock_jira_client.issue.side_effect = JIRAError(status_code=404, text="Issue does not exist")

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--comment", "test"])

    assert result.exit_code == 1
    assert "Erreur" in result.output
