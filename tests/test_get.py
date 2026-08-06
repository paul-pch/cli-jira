from types import SimpleNamespace
from unittest.mock import MagicMock

from jira.client import ResultList

from main import app
from tests.conftest import make_issue, runner


def test_projects(mock_jira_client: MagicMock) -> None:
    mock_jira_client.projects.return_value = [
        SimpleNamespace(key="ST", name="Socle Technique"),
        SimpleNamespace(key="OPS", name="Operations"),
    ]

    result = runner.invoke(app, ["get", "projects"])

    assert result.exit_code == 0
    assert "ST" in result.output
    assert "Socle Technique" in result.output


def test_issue(mock_jira_client: MagicMock) -> None:
    mock_jira_client.issue.return_value = make_issue(key="ST-1060", summary="Titre du ticket")
    mock_jira_client.remote_links.return_value = []

    result = runner.invoke(app, ["get", "issue", "ST-1060"])

    assert result.exit_code == 0
    assert "ST-1060" in result.output
    assert "Titre du ticket" in result.output
    mock_jira_client.issue.assert_called_once_with(
        "ST-1060",
        fields="key,description,summary,issuetype,assignee,status,created,labels",
    )


def test_issues(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = [
        make_issue(key="ST-1", summary="Premier ticket"),
        make_issue(key="ST-2", summary="Second ticket"),
    ]

    result = runner.invoke(app, ["get", "issues"])

    assert result.exit_code == 0
    assert "ST-1" in result.output
    assert "ST-2" in result.output
    mock_jira_client.search_issues.assert_called_once()


def test_issues_all(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = [
        make_issue(key="ST-1", summary="Premier ticket"),
    ]

    result = runner.invoke(app, ["get", "issues", "--all"])

    assert result.exit_code == 0
    jql = mock_jira_client.search_issues.call_args[0][0]
    assert "currentUser()" not in jql
    assert 'project = "ST"' in jql


def test_issues_truncated_warns(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = ResultList(
        [make_issue(key="ST-1")],
        _total=42,
    )

    result = runner.invoke(app, ["get", "issues"])

    assert result.exit_code == 0
    assert "tronqué" in result.output
    assert "1 ticket(s) sur 42" in result.output


def test_issues_not_truncated_no_warning(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = ResultList(
        [make_issue(key="ST-1")],
        _total=1,
    )

    result = runner.invoke(app, ["get", "issues"])

    assert result.exit_code == 0
    assert "tronqué" not in result.output


def test_status(mock_jira_client: MagicMock) -> None:
    mock_jira_client.issue.return_value = make_issue(issuetype="Story Technique")
    mock_jira_client.transitions.return_value = [{"id": "1", "name": "En cours"}, {"id": "2", "name": "Terminé"}]

    result = runner.invoke(app, ["get", "status", "ST-1"])

    assert result.exit_code == 0
    assert "En cours" in result.output
    assert "Terminé" in result.output


def test_status_no_arg_uses_default_issue_type(mock_jira_client: MagicMock) -> None:
    mock_jira_client._get_json.return_value = [  # noqa: SLF001
        {
            "name": "Story Technique",
            "statuses": [{"name": "A faire"}, {"name": "En cours"}, {"name": "Terminé"}],
        },
        {"name": "Bug", "statuses": [{"name": "Ouvert"}, {"name": "Fermé"}]},
    ]

    result = runner.invoke(app, ["get", "status"])

    assert result.exit_code == 0
    assert "A faire" in result.output
    assert "En cours" in result.output
    assert "Terminé" in result.output
    assert "Ouvert" not in result.output
    mock_jira_client._get_json.assert_called_once_with("project/ST/statuses")  # noqa: SLF001


def test_status_no_arg_unknown_default_issue_type(mock_jira_client: MagicMock) -> None:
    mock_jira_client._get_json.return_value = [  # noqa: SLF001
        {"name": "Bug", "statuses": [{"name": "Ouvert"}]},
    ]

    result = runner.invoke(app, ["get", "status"])

    assert result.exit_code == 1
    assert "introuvable" in result.output


def test_users_found(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_users.return_value = [MagicMock(displayName="Jean Dupont", accountId="acc-1")]

    result = runner.invoke(app, ["get", "users", "--query", "jean"])

    assert result.exit_code == 0
    assert "Jean Dupont" in result.output
    assert "acc-1" in result.output


def test_users_not_found(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_users.return_value = []

    result = runner.invoke(app, ["get", "users", "--query", "personne"])

    assert result.exit_code == 1
    assert "No user found." in result.output
