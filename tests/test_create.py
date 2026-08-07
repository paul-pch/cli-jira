from types import SimpleNamespace
from unittest.mock import MagicMock, call

from app.utils.issue_fields import ISSUE_FIELDS, issue_fields
from main import app
from tests.conftest import SPRINT_FIELD, make_issue, make_sprint, runner, with_active_sprint, with_sprint_field


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


def test_issue_with_status(mock_jira_client: MagicMock) -> None:
    created = make_issue(key="ST-42")
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = created
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]
    mock_jira_client.issue.return_value = make_issue(key="ST-42", status="en cours")

    result = runner.invoke(app, ["create", "issue", "Titre", "--status", "EN COURS"])

    assert result.exit_code == 0
    mock_jira_client.transition_issue.assert_called_once_with(created, "31")
    mock_jira_client.issue.assert_called_once_with("ST-42", fields=ISSUE_FIELDS)
    assert "en cours" in result.output


def test_issue_with_unknown_status(mock_jira_client: MagicMock) -> None:
    """The issue is already created at that point — only the transition fails."""
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue(key="ST-42")
    mock_jira_client.transitions.return_value = [{"id": "31", "name": "en cours"}]

    result = runner.invoke(app, ["create", "issue", "Titre", "--status", "Statut inconnu"])

    assert result.exit_code == 1
    assert "Statut inconnu" in result.output
    assert "en cours" in result.output
    mock_jira_client.create_issue.assert_called_once()
    mock_jira_client.transition_issue.assert_not_called()


def test_issue_without_status_does_not_transition(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre"])

    assert result.exit_code == 0
    mock_jira_client.transitions.assert_not_called()
    mock_jira_client.transition_issue.assert_not_called()


def test_issue_with_links(mock_jira_client: MagicMock) -> None:
    created = make_issue(key="ST-42")
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = created
    mock_jira_client.remote_links.return_value = []

    result = runner.invoke(
        app,
        ["create", "issue", "Titre", "--link", "https://example.com", "--link", "MR=https://gitlab.com/x/1"],
    )

    assert result.exit_code == 0
    assert mock_jira_client.add_simple_link.call_args_list == [
        call(created, object={"url": "https://example.com", "title": "https://example.com"}),
        call(created, object={"url": "https://gitlab.com/x/1", "title": "MR"}),
    ]


def test_issue_with_invalid_link_creates_nothing(mock_jira_client: MagicMock) -> None:
    """The link is parsed up front so a typo doesn't leave a half-configured issue behind."""
    result = runner.invoke(app, ["create", "issue", "Titre", "--link", "example.com"])

    assert result.exit_code == 1
    assert "lien invalide" in result.output
    mock_jira_client.create_issue.assert_not_called()


def test_issue_without_link_does_not_touch_remote_links(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre"])

    assert result.exit_code == 0
    mock_jira_client.add_simple_link.assert_not_called()
    mock_jira_client.remote_links.assert_not_called()


def test_issue_goes_to_the_active_sprint_by_default(mock_jira_client: MagicMock) -> None:
    created = make_issue(key="ST-42")
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = created
    mock_jira_client.issue.return_value = created
    with_active_sprint(mock_jira_client, make_sprint(sprint_id=42))

    result = runner.invoke(app, ["create", "issue", "Titre"])

    assert result.exit_code == 0
    mock_jira_client.add_issues_to_sprint.assert_called_once_with(42, ["ST-42"])


def test_issue_refetched_to_show_the_sprint_it_landed_in(mock_jira_client: MagicMock) -> None:
    """The sprint is applied after creation, so what `create_issue` returned is already stale."""
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue(key="ST-42")
    mock_jira_client.issue.return_value = make_issue(key="ST-42", sprint=[SimpleNamespace(name="Sprint 10")])
    with_active_sprint(mock_jira_client)
    with_sprint_field(mock_jira_client)

    result = runner.invoke(app, ["create", "issue", "Titre"])

    assert result.exit_code == 0
    assert "Sprint 10" in result.output
    mock_jira_client.issue.assert_called_once_with("ST-42", fields=issue_fields(SPRINT_FIELD))


def test_issue_with_a_named_sprint(mock_jira_client: MagicMock) -> None:
    created = make_issue(key="ST-42")
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = created
    mock_jira_client.issue.return_value = created
    with_active_sprint(mock_jira_client, make_sprint(sprint_id=7, name="Sprint 11", state="future"))

    result = runner.invoke(app, ["create", "issue", "Titre", "--sprint", "Sprint 11"])

    assert result.exit_code == 0
    mock_jira_client.add_issues_to_sprint.assert_called_once_with(7, ["ST-42"])


def test_no_sprint_creates_in_the_backlog(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre", "--no-sprint"])

    assert result.exit_code == 0
    mock_jira_client.boards.assert_not_called()
    mock_jira_client.add_issues_to_sprint.assert_not_called()


def test_issue_created_even_without_a_running_sprint(mock_jira_client: MagicMock) -> None:
    """The implicit default must not block creation on a project that has no sprint."""
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue(key="ST-42")
    mock_jira_client.boards.return_value = []

    result = runner.invoke(app, ["create", "issue", "Titre"])

    assert result.exit_code == 0
    assert "backlog" in result.output
    mock_jira_client.create_issue.assert_called_once()
    mock_jira_client.add_issues_to_sprint.assert_not_called()


def test_explicit_unknown_sprint_creates_nothing(mock_jira_client: MagicMock) -> None:
    """An explicit --sprint is worth failing on, and is resolved before anything is written."""
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    with_active_sprint(mock_jira_client, make_sprint(name="Sprint 10"))

    result = runner.invoke(app, ["create", "issue", "Titre", "--sprint", "Sprint 11"])

    assert result.exit_code == 1
    assert "sprint introuvable" in result.output
    assert "Sprint 10" in result.output
    mock_jira_client.create_issue.assert_not_called()


def test_issue_with_estimate(mock_jira_client: MagicMock) -> None:
    mock_jira_client.myself.return_value = {"accountId": "acc-me"}
    mock_jira_client.create_issue.return_value = make_issue()

    result = runner.invoke(app, ["create", "issue", "Titre", "--estimate", "2h"])

    assert result.exit_code == 0
    fields = mock_jira_client.create_issue.call_args.kwargs["fields"]
    assert fields["timetracking"] == {"estimate": "2h"}
