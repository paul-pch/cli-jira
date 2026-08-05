from unittest.mock import MagicMock

from app.utils.exceptions import InvalidJiraStatusError
from main import app
from tests.conftest import make_issue, runner


def test_nothing_to_update(mock_jira_client: MagicMock) -> None:
    result = runner.invoke(app, ["edit", "issue", "ST-1"])

    assert result.exit_code == 1
    assert "Nothing to update" in result.output
    mock_jira_client.issue.assert_not_called()


def test_status_transition(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    mock_jira_client.issue.return_value = issue
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--status", "En Cours"])

    assert result.exit_code == 0
    mock_jira_client.transition_issue.assert_called_once_with(issue, "31")


def test_invalid_status_is_not_caught(mock_jira_client: MagicMock) -> None:
    """Documents current behavior.

    InvalidJiraStatusError isn't part of the caught exception tuple in app/edit.py, so it
    surfaces as an uncaught exception instead of a friendly message. See TODO.md.
    """
    mock_jira_client.issue.return_value = make_issue(key="ST-1")
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--status", "Statut inconnu"])

    assert result.exit_code == 1
    assert isinstance(result.exception, InvalidJiraStatusError)
    mock_jira_client.transition_issue.assert_not_called()


def test_comment_only(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--comment", "Un commentaire"])

    assert result.exit_code == 0
    mock_jira_client.add_comment.assert_called_once_with(issue, "Un commentaire")
    mock_jira_client.transition_issue.assert_not_called()


def test_description_only(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--description", "Nouvelle description"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(description="Nouvelle description")


def test_description_and_comment(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--description", "Nouvelle desc", "--comment", "Un commentaire"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(description="Nouvelle desc")
    mock_jira_client.add_comment.assert_called_once_with(issue, "Un commentaire")
