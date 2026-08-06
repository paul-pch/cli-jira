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
) -> SimpleNamespace:
    """Build a fake `jira.Issue` shaped exactly as `app/utils/display.py` expects it."""
    assignee = SimpleNamespace(displayName=assignee_name) if assignee_name else None
    fields = SimpleNamespace(
        summary=summary,
        status=SimpleNamespace(name=status),
        issuetype=SimpleNamespace(name=issuetype),
        assignee=assignee,
        labels=labels or [],
        description=description,
        created=created,
        timetracking=timetracking or {},
        issuelinks=issuelinks or [],
    )
    return SimpleNamespace(key=key, fields=fields)


def make_issue_link(relation: str = "blocks", other_key: str = "ST-2", *, outward: bool = True) -> SimpleNamespace:
    """Build a fake issue link, shaped as `IssueView._links` expects it."""
    other = SimpleNamespace(key=other_key)
    link_type = SimpleNamespace(outward=relation, inward=relation, name=relation.capitalize())

    if outward:
        return SimpleNamespace(type=link_type, outwardIssue=other)

    return SimpleNamespace(type=link_type, inwardIssue=other)
