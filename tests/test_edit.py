from unittest.mock import MagicMock

from main import app
from tests.conftest import make_issue, runner


def test_nothing_to_update(mock_jira_client: MagicMock) -> None:
    result = runner.invoke(app, ["edit", "issue", "ST-1"])

    assert result.exit_code == 1
    assert "aucune modification" in result.output
    mock_jira_client.issue.assert_not_called()


def test_status_transition(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    mock_jira_client.issue.return_value = issue
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--status", "En Cours"])

    assert result.exit_code == 0
    mock_jira_client.transition_issue.assert_called_once_with(issue, "31")


def test_invalid_status_reports_the_available_ones(mock_jira_client: MagicMock) -> None:
    """InvalidJiraStatusError used to surface as a raw traceback; it is now a friendly message."""
    mock_jira_client.issue.return_value = make_issue(key="ST-1")
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--status", "Statut inconnu"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "Statut inconnu" in result.output
    assert "en cours" in result.output
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
    issue.update.assert_called_once_with(fields={"description": "Nouvelle description"})


def test_description_and_comment(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--description", "Nouvelle desc", "--comment", "Un commentaire"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"description": "Nouvelle desc"})
    mock_jira_client.add_comment.assert_called_once_with(issue, "Un commentaire")


def test_description_and_estimate_are_sent_in_one_call(mock_jira_client: MagicMock) -> None:
    """Both used to go through two separate `issue.update` round-trips."""
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--description", "Nouvelle desc", "--estimate", "3h"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"description": "Nouvelle desc", "timetracking": {"estimate": "3h"}})


def test_estimate_only(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=issue)
    mock_jira_client.issue.return_value = issue
    mock_jira_client.search_users.return_value = []

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--estimate", "3h"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"timetracking": {"estimate": "3h"}})
