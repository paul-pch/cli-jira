import typer
from jira import JIRA, Issue, JIRAError

from app.utils.exceptions import AmbiguousUserError, IssueTypeNotFoundError, UserNotFoundError


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
