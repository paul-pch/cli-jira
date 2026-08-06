import typer
from jira import JIRA, Issue, JIRAError

from app.utils.exceptions import (
    AmbiguousUserError,
    InvalidIssueLinkTypeError,
    InvalidJiraStatusError,
    IssueTypeNotFoundError,
    UserNotFoundError,
)


def get_jira_client(required_envs: dict[str, str]) -> JIRA:
    try:
        return JIRA(basic_auth=(required_envs["user"], required_envs["token"]), server=required_envs["server"], timeout=5)

    except JIRAError as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


def get_transitions_from_issue(jira: JIRA, issue: Issue) -> list[str]:
    return [status["name"] for status in jira.transitions(issue)]


def get_statuses_for_issue_type(jira: JIRA, project: str, issue_type: str) -> list[str]:
    """Fetch the possible statuses for an issue type, in the given project."""
    issue_types = jira._get_json(f"project/{project}/statuses")  # noqa: SLF001
    matching = next((it for it in issue_types if it["name"] == issue_type), None)

    if matching is None:
        raise IssueTypeNotFoundError(issue_type, project)

    return [status["name"] for status in matching["statuses"]]


def transition_to_status(jira: JIRA, issue: Issue, status: str) -> None:
    """Move an issue to a status, matching the transition name case-insensitively."""
    transitions = jira.transitions(issue)
    transition_id = next((t["id"] for t in transitions if t["name"].lower() == status.lower()), None)

    if not transition_id:
        raise InvalidJiraStatusError(status, [t["name"] for t in transitions])

    jira.transition_issue(issue, transition_id)


def resolve_link_type(jira: JIRA, wanted: str) -> str:
    """Resolve a link type to the exact string Jira knows, matching name or direction wording.

    Matching the outward wording ("blocks") keeps the direction, the inward one
    ("is blocked by") makes the lib swap the two issues.
    """
    known = jira.issue_link_types()
    lowered = wanted.lower()

    for attribute in ("name", "outward", "inward"):
        for link_type in known:
            if lowered == getattr(link_type, attribute).lower():
                return str(getattr(link_type, attribute))

    raise InvalidIssueLinkTypeError(wanted, [t.name for t in known])


def link_issues(jira: JIRA, issue: Issue, link_type: str, targets: list[str]) -> None:
    """Link an issue to others, the current issue being the one the relation starts from."""
    resolved = resolve_link_type(jira, link_type)

    for target in targets:
        jira.create_issue_link(type=resolved, inwardIssue=issue.key, outwardIssue=target)


def resolve_assignee(jira: JIRA, owned: bool, owner: str | None) -> dict[str, str] | None:
    """Resolve the account to assign an issue to.

    `owner` takes precedence over `owned`; returns None when neither is requested.
    """
    if owner:
        users = jira.search_users(query=owner)
        if not users:
            raise UserNotFoundError(owner)
        if len(users) > 1:
            raise AmbiguousUserError(owner)
        return {"id": users[0].accountId}

    if owned:
        # Jira token account
        return {"id": jira.myself()["accountId"]}

    return None
