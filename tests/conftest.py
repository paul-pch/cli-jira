from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from jira import JIRA
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def jira_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JIRA_URL", "https://jira.example.com")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_TOKEN", "secrettoken")


@pytest.fixture
def mock_jira_client(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch AppState's jira client so no command ever hits a real Jira server."""
    request.getfixturevalue("jira_env")
    client = MagicMock(spec=JIRA)
    monkeypatch.setattr("app.utils.jira.get_jira_client", lambda _env_vars: client)
    return client


def make_issue(
    key: str = "ST-1",
    summary: str = "Summary",
    status: str = "A faire",
    issuetype: str = "Story Technique",
    assignee_name: str | None = "Jean Dupont",
    labels: list[str] | None = None,
    description: str | None = "Description",
    created: str = "2024-01-01T00:00:00.000+0000",
    timetracking: dict | None = None,
    issuelinks: list | None = None,
    comments: list | None = None,
    project: str = "ST",
) -> SimpleNamespace:
    """Build a fake `jira.Issue` shaped exactly as `app/utils/display.py` expects it."""
    assignee = SimpleNamespace(displayName=assignee_name) if assignee_name else None
    fields = SimpleNamespace(
        project=SimpleNamespace(key=project),
        summary=summary,
        status=SimpleNamespace(name=status),
        issuetype=SimpleNamespace(name=issuetype),
        assignee=assignee,
        labels=labels or [],
        description=description,
        created=created,
        timetracking=timetracking or {},
        issuelinks=issuelinks or [],
        comment=SimpleNamespace(comments=comments or []),
    )
    return SimpleNamespace(key=key, fields=fields)


def make_comment(
    author: str | None = "Jean Dupont",
    body: str = "Un commentaire",
    created: str = "2024-01-02T00:00:00.000+0000",
) -> SimpleNamespace:
    """Build a fake comment, shaped as `IssueView._comments` expects it."""
    return SimpleNamespace(
        author=SimpleNamespace(displayName=author) if author else None,
        body=body,
        created=created,
    )


def make_sprint(sprint_id: int = 42, name: str = "Sprint 10", state: str = "active") -> SimpleNamespace:
    """Build a fake `jira.resources.Sprint`, shaped as `app/utils/sprints.py` reads it."""
    return SimpleNamespace(id=sprint_id, name=name, state=state)


def make_board(board_id: int = 7, name: str = "ST Scrum") -> SimpleNamespace:
    """Build a fake `jira.resources.Board`, shaped as `app/utils/sprints.py` reads it."""
    return SimpleNamespace(id=board_id, name=name)


def with_active_sprint(client: MagicMock, sprint: SimpleNamespace | None = None) -> SimpleNamespace:
    """Wire a client so sprint resolution finds one board and one running sprint."""
    sprint = sprint or make_sprint()
    client.boards.return_value = [make_board()]
    client.sprints.return_value = [sprint]
    return sprint


def make_issue_link(relation: str = "blocks", other_key: str = "ST-2", *, outward: bool = True) -> SimpleNamespace:
    """Build a fake issue link, shaped as `IssueView._links` expects it."""
    other = SimpleNamespace(key=other_key)
    link_type = SimpleNamespace(outward=relation, inward=relation, name=relation.capitalize())

    if outward:
        return SimpleNamespace(type=link_type, outwardIssue=other)

    return SimpleNamespace(type=link_type, inwardIssue=other)
