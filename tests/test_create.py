from unittest.mock import MagicMock

from main import app
from tests.conftest import make_issue, runner


def test_issue_owned_by_default(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue(key="ST-42", summary="Titre")

    result = runner.invoke(app, ["create", "issue", "Titre"])

    assert result.exit_code == 0
    assert "ST-42" in result.output
    mock_jira_client.myself.assert_called_once()
    fields = mock_jira_client.create_issue.call_args.kwargs["fields"]
    assert fields["assignee"] == {"id": "acc-me"}
    assert fields["summary"] == "Titre"
    assert fields["project"] == {"key": "ST"}
    assert fields["issuetype"] == {"name": "Story Technique"}


def test_issue_labels_merged_with_config_defaults(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre", "--labels", "foo"])

    assert result.exit_code == 0
    fields = mock_jira_client.create_issue.call_args.kwargs["fields"]
    assert fields["labels"] == ["foo", "OPS", "Cycle10"]


def test_issue_with_parent(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre", "--parent", "ST-1"])

    assert result.exit_code == 0
    fields = mock_jira_client.create_issue.call_args.kwargs["fields"]
    assert fields["parent"] == {"key": "ST-1"}


def test_issue_with_owner_single_match(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_users.return_value = [MagicMock(accountId="acc-owner")]
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre", "--no-owned", "--owner", "michel"])

    assert result.exit_code == 0
    mock_jira_client.myself.assert_not_called()
    fields = mock_jira_client.create_issue.call_args.kwargs["fields"]
    assert fields["assignee"] == {"id": "acc-owner"}


def test_issue_with_owner_too_many_matches(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_users.return_value = [MagicMock(), MagicMock()]

    result = runner.invoke(app, ["create", "issue", "Titre", "--no-owned", "--owner", "michel"])

    assert result.exit_code == 1
    assert "plusieurs utilisateurs" in result.output
    mock_jira_client.create_issue.assert_not_called()


def test_issue_with_owner_no_match(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_users.return_value = []

    result = runner.invoke(app, ["create", "issue", "Titre", "--no-owned", "--owner", "michel"])

    assert result.exit_code == 1
    assert "aucun utilisateur" in result.output
    mock_jira_client.create_issue.assert_not_called()


def test_issue_with_estimate(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre", "--estimate", "2h"])

    assert result.exit_code == 0
    fields = mock_jira_client.create_issue.call_args.kwargs["fields"]
    assert fields["timetracking"] == {"estimate": "2h"}
