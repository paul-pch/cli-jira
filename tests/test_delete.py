from unittest.mock import MagicMock

from main import app
from tests.conftest import make_issue, runner


def test_delete_asks_for_confirmation(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1", summary="Titre du ticket")
    issue.delete = MagicMock()
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["delete", "issue", "ST-1"], input="y\n")

    assert result.exit_code == 0
    assert "ST-1" in result.output
    assert "Titre du ticket" in result.output
    issue.delete.assert_called_once_with(deleteSubtasks=False)


def test_delete_refused_leaves_the_issue_alone(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.delete = MagicMock()
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["delete", "issue", "ST-1"], input="n\n")

    assert result.exit_code == 1
    assert "annulée" in result.output
    issue.delete.assert_not_called()


def test_delete_yes_skips_the_prompt(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.delete = MagicMock()
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["delete", "issue", "ST-1", "--yes"])

    assert result.exit_code == 0
    assert "Supprimer définitivement" not in result.output
    issue.delete.assert_called_once_with(deleteSubtasks=False)


def test_delete_with_subtasks(mock_jira_client: MagicMock) -> None:
    """Jira refuses to delete an issue that still has subtasks unless asked explicitly."""
    issue = make_issue(key="ST-1")
    issue.delete = MagicMock()
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["delete", "issue", "ST-1", "--yes", "--with-subtasks"])

    assert result.exit_code == 0
    issue.delete.assert_called_once_with(deleteSubtasks=True)
