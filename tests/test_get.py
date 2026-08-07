from types import SimpleNamespace
from unittest.mock import MagicMock

from jira.client import ResultList

from app.utils.issue_fields import ISSUE_FIELDS, issue_fields
from main import app
from tests.conftest import (
    SPRINT_FIELD,
    make_comment,
    make_issue,
    make_sprint,
    runner,
    with_active_sprint,
    with_sprint_field,
)


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
    mock_jira_client.issue.assert_called_once_with("ST-1060", fields=ISSUE_FIELDS)


def test_issue_shows_its_sprint(mock_jira_client: MagicMock) -> None:
    with_sprint_field(mock_jira_client)
    mock_jira_client.issue.return_value = make_issue(sprint=[SimpleNamespace(name="Sprint 10", state="active")])
    mock_jira_client.remote_links.return_value = []

    result = runner.invoke(app, ["get", "issue", "ST-1"])

    assert result.exit_code == 0
    assert "Sprint 10" in result.output
    mock_jira_client.issue.assert_called_once_with("ST-1", fields=issue_fields(SPRINT_FIELD))


def test_issue_without_a_sprint_field_on_the_instance(mock_jira_client: MagicMock) -> None:
    """No sprint field, no sprint column, and the plain field list is requested."""
    mock_jira_client.fields.return_value = [{"id": "summary"}]
    mock_jira_client.issue.return_value = make_issue()
    mock_jira_client.remote_links.return_value = []

    result = runner.invoke(app, ["get", "issue", "ST-1"])

    assert result.exit_code == 0
    mock_jira_client.issue.assert_called_once_with("ST-1", fields=ISSUE_FIELDS)


def test_issue_shows_its_comments(mock_jira_client: MagicMock) -> None:
    mock_jira_client.issue.return_value = make_issue(
        comments=[make_comment(author="Jean Dupont", body="Un commentaire utile")],
    )
    mock_jira_client.remote_links.return_value = []

    result = runner.invoke(app, ["get", "issue", "ST-1"])

    assert result.exit_code == 0
    assert "Jean Dupont" in result.output
    assert "Un commentaire utile" in result.output


def test_issue_shows_the_estimate(mock_jira_client: MagicMock) -> None:
    """The estimate was fetched but never rendered."""
    mock_jira_client.issue.return_value = make_issue(timetracking={"originalEstimate": "3h"})
    mock_jira_client.remote_links.return_value = []

    result = runner.invoke(app, ["get", "issue", "ST-1"])

    assert result.exit_code == 0
    assert "3h" in result.output


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


def test_issues_filtered_by_project_and_status(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = [make_issue(key="OPS-1")]

    result = runner.invoke(app, ["get", "issues", "--project", "OPS", "--status", "EN COURS", "--status", "Terminé"])

    assert result.exit_code == 0
    jql = mock_jira_client.search_issues.call_args[0][0]
    assert 'project = "OPS"' in jql
    assert 'status in ("EN COURS", "Terminé")' in jql
    assert "not in" not in jql


def test_issues_filtered_by_assignee(mock_jira_client: MagicMock) -> None:
    """JQL matches users by account id on Jira Cloud, so the name is resolved first."""
    mock_jira_client.search_users.return_value = [MagicMock(accountId="acc-michel")]
    mock_jira_client.search_issues.return_value = [make_issue(key="ST-1")]

    result = runner.invoke(app, ["get", "issues", "--assignee", "michel"])

    assert result.exit_code == 0
    jql = mock_jira_client.search_issues.call_args[0][0]
    assert 'assignee = "acc-michel"' in jql
    assert "currentUser()" not in jql


def test_issues_unknown_assignee_does_not_search(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_users.return_value = []

    result = runner.invoke(app, ["get", "issues", "--assignee", "personne"])

    assert result.exit_code == 1
    assert "aucun utilisateur" in result.output
    mock_jira_client.search_issues.assert_not_called()


def test_issues_with_raw_jql(mock_jira_client: MagicMock) -> None:
    """The query is passed through untouched, ORDER BY included."""
    mock_jira_client.search_issues.return_value = [make_issue(key="ST-1")]
    raw = "labels = OPS ORDER BY created ASC"

    result = runner.invoke(app, ["get", "issues", "--jql", raw])

    assert result.exit_code == 0
    assert mock_jira_client.search_issues.call_args[0][0] == raw
    mock_jira_client.search_users.assert_not_called()


def test_raw_jql_conflicts_with_the_filter_options(mock_jira_client: MagicMock) -> None:
    result = runner.invoke(app, ["get", "issues", "--jql", "labels = OPS", "--project", "OPS"])

    assert result.exit_code == 1
    assert "--jql" in result.output
    mock_jira_client.search_issues.assert_not_called()


def test_issues_filtered_by_sprint(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = [make_issue(key="ST-1")]
    with_active_sprint(mock_jira_client, make_sprint(sprint_id=42))

    result = runner.invoke(app, ["get", "issues", "--sprint", "current"])

    assert result.exit_code == 0
    assert "sprint = 42" in mock_jira_client.search_issues.call_args[0][0]


def test_sprint_filter_conflicts_with_raw_jql(mock_jira_client: MagicMock) -> None:
    result = runner.invoke(app, ["get", "issues", "--jql", "labels = OPS", "--sprint", "current"])

    assert result.exit_code == 1
    assert "--jql" in result.output
    mock_jira_client.search_issues.assert_not_called()


def test_sprints_lists_the_board_sprints(mock_jira_client: MagicMock) -> None:
    with_active_sprint(mock_jira_client, make_sprint(sprint_id=42, name="Sprint 10"))

    result = runner.invoke(app, ["get", "sprints"])

    assert result.exit_code == 0
    assert "Sprint 10" in result.output
    assert "42" in result.output
    mock_jira_client.boards.assert_called_once_with(projectKeyOrID="ST", type="scrum", name=None)
    mock_jira_client.sprints.assert_called_once_with(7, state="active,future")


def test_sprints_with_an_explicit_state(mock_jira_client: MagicMock) -> None:
    """Closed sprints are listed on demand: their id is the only way to filter on them."""
    with_active_sprint(mock_jira_client, make_sprint(name="Sprint 9", state="closed"))

    result = runner.invoke(app, ["get", "sprints", "--state", "closed"])

    assert result.exit_code == 0
    mock_jira_client.sprints.assert_called_once_with(7, state="closed")


def test_sprints_without_a_board(mock_jira_client: MagicMock) -> None:
    mock_jira_client.boards.return_value = []

    result = runner.invoke(app, ["get", "sprints"])

    assert result.exit_code == 1
    assert "tableau scrum" in result.output


def test_issues_more_to_come_suggests_the_next_page(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = ResultList(
        [make_issue(key="ST-1")],
        _total=42,
    )

    result = runner.invoke(app, ["get", "issues"])

    assert result.exit_code == 0
    assert "Tickets 1-1 sur 42" in result.output
    assert "--start 1" in result.output


def test_issues_pagination_is_passed_to_jira(mock_jira_client: MagicMock) -> None:
    mock_jira_client.search_issues.return_value = ResultList([make_issue(key="ST-11")], _total=42)

    page_size = 10

    result = runner.invoke(app, ["get", "issues", "--limit", str(page_size), "--start", str(page_size)])

    assert result.exit_code == 0
    assert mock_jira_client.search_issues.call_args.kwargs["startAt"] == page_size
    assert mock_jira_client.search_issues.call_args.kwargs["maxResults"] == page_size
    assert "Tickets 11-11 sur 42" in result.output
    assert "--start 11" in result.output


def test_issues_past_the_last_page(mock_jira_client: MagicMock) -> None:
    """An out-of-range --start returns nothing, which shouldn't look like an empty project."""
    mock_jira_client.search_issues.return_value = ResultList([], _total=42)

    result = runner.invoke(app, ["get", "issues", "--start", "100"])

    assert result.exit_code == 0
    assert "Aucun ticket à partir de l'index 100" in result.output


def test_issues_limit_defaults_to_the_config(mock_jira_client: MagicMock) -> None:
    configured_max_result = 50
    mock_jira_client.search_issues.return_value = ResultList([make_issue(key="ST-1")], _total=1)

    result = runner.invoke(app, ["get", "issues"])

    assert result.exit_code == 0
    assert mock_jira_client.search_issues.call_args.kwargs["maxResults"] == configured_max_result


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


def test_status_for_another_issue_type(mock_jira_client: MagicMock) -> None:
    mock_jira_client._get_json.return_value = [  # noqa: SLF001
        {"name": "Story Technique", "statuses": [{"name": "A faire"}]},
        {"name": "Bug", "statuses": [{"name": "Ouvert"}, {"name": "Fermé"}]},
    ]

    result = runner.invoke(app, ["get", "status", "--issue-type", "Bug"])

    assert result.exit_code == 0
    assert "Ouvert" in result.output
    assert "Fermé" in result.output
    assert "A faire" not in result.output


def test_status_for_another_project(mock_jira_client: MagicMock) -> None:
    mock_jira_client._get_json.return_value = [  # noqa: SLF001
        {"name": "Story Technique", "statuses": [{"name": "A faire"}]},
    ]

    result = runner.invoke(app, ["get", "status", "--project", "OPS"])

    assert result.exit_code == 0
    mock_jira_client._get_json.assert_called_once_with("project/OPS/statuses")  # noqa: SLF001


def test_status_unknown_issue_type(mock_jira_client: MagicMock) -> None:
    mock_jira_client._get_json.return_value = [  # noqa: SLF001
        {"name": "Bug", "statuses": [{"name": "Ouvert"}]},
    ]

    result = runner.invoke(app, ["get", "status", "--issue-type", "Épopée"])

    assert result.exit_code == 1
    assert "Épopée" in result.output
    assert "introuvable" in result.output


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
    assert "aucun utilisateur" in result.output
