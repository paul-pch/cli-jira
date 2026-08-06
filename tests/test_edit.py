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


def test_title_only(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--title", "Nouveau titre"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"summary": "Nouveau titre"}, update={})


def test_title_with_other_fields_is_one_call(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--title", "Nouveau titre", "--labels", "OPS"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(
        fields={"summary": "Nouveau titre"},
        update={"labels": [{"add": "OPS"}]},
    )


def test_reassign_to_a_named_owner(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue
    mock_jira_client.search_users.return_value = [MagicMock(accountId="acc-owner")]

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--owner", "michel"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"assignee": {"id": "acc-owner"}}, update={})
    mock_jira_client.myself.assert_not_called()


def test_reassign_to_self(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--owned"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"assignee": {"id": "acc-me"}}, update={})


def test_other_edits_leave_the_assignee_alone(mock_jira_client: MagicMock) -> None:
    """Without --owned/--owner the assignee must not be touched, unlike at creation."""
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--title", "Nouveau titre"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"summary": "Nouveau titre"}, update={})
    mock_jira_client.myself.assert_not_called()


def test_unknown_owner_writes_nothing(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]
    mock_jira_client.search_users.return_value = []

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--owner", "personne", "--status", "en cours"])

    assert result.exit_code == 1
    assert "aucun utilisateur" in result.output
    issue.update.assert_not_called()
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
    issue.update.assert_called_once_with(fields={"description": "Nouvelle description"}, update={})


def test_description_and_comment(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--description", "Nouvelle desc", "--comment", "Un commentaire"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"description": "Nouvelle desc"}, update={})
    mock_jira_client.add_comment.assert_called_once_with(issue, "Un commentaire")


def test_description_and_estimate_are_sent_in_one_call(mock_jira_client: MagicMock) -> None:
    """Both used to go through two separate `issue.update` round-trips."""
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--description", "Nouvelle desc", "--estimate", "3h"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"description": "Nouvelle desc", "timetracking": {"estimate": "3h"}}, update={})


def test_add_and_remove_labels(mock_jira_client: MagicMock) -> None:
    """Partial edits go through the `update` verb, so Jira applies them without a read-modify-write."""
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--labels", "OPS", "--remove-labels", "Cycle10"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={}, update={"labels": [{"add": "OPS"}, {"remove": "Cycle10"}]})


def test_labels_are_cumulative(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=True)
    mock_jira_client.issue.return_value = issue

    result = runner.invoke(
        app,
        ["edit", "issue", "ST-1", "--labels", "OPS", "--labels", "Cycle11", "--remove-labels", "Cycle10"],
    )

    assert result.exit_code == 0
    issue.update.assert_called_once_with(
        fields={},
        update={"labels": [{"add": "OPS"}, {"add": "Cycle11"}, {"remove": "Cycle10"}]},
    )


def test_estimate_only(mock_jira_client: MagicMock) -> None:
    issue = make_issue(key="ST-1")
    issue.update = MagicMock(return_value=issue)
    mock_jira_client.issue.return_value = issue
    mock_jira_client.search_users.return_value = []

    result = runner.invoke(app, ["edit", "issue", "ST-1", "--estimate", "3h"])

    assert result.exit_code == 0
    issue.update.assert_called_once_with(fields={"timetracking": {"estimate": "3h"}}, update={})
