from typing import TYPE_CHECKING, Annotated, Optional

import typer
from rich.console import Console

from app.utils import display
from app.utils.errors import handle_jira_errors
from app.utils.exceptions import UserNotFoundError
from app.utils.issue_fields import ISSUE_FIELDS
from app.utils.jira import get_statuses_for_issue_type, get_transitions_from_issue, resolve_assignee
from app.utils.jql import build_issues_jql

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Get a specific ressource")
console = Console()


@app.command()
@handle_jira_errors
def issue(ctx: typer.Context, issue_key: Annotated[str, typer.Argument(help="The code of the issue")]) -> None:
    """Get a specific issue.

    Example: jira get issue ST-1060
    """
    jira = ctx.obj.jira_client

    issue: Issue = jira.issue(issue_key, fields=ISSUE_FIELDS)
    remote_links = jira.remote_links(issue_key)

    display.display_issue(issue, remote_links)


@app.command()
@handle_jira_errors
def issues(
    ctx: typer.Context,
    all_users: Annotated[
        bool, typer.Option("--all", help="Récupérer les tickets de tous les utilisateurs, pas seulement les siens.")
    ] = False,
    project: Annotated[
        Optional[str],
        typer.Option(help="Code du projet. Par défaut celui de config.toml."),
    ] = None,
    status: Annotated[
        Optional[list[str]],
        typer.Option(help="Ne garder que ces statuts. Répétable. Remplace le filtre par défaut sur les statuts fermés."),
    ] = None,
    assignee: Annotated[
        Optional[str],
        typer.Option(help="Ne garder que les tickets de cet utilisateur. Prioritaire sur --all."),
    ] = None,
) -> None:
    """List issues.

    Example: jira get issues
    Example: jira get issues --all
    Example: jira get issues --project ST --status 'EN COURS'
    Example: jira get issues --assignee michel
    """
    jira = ctx.obj.jira_client

    # Resolved to an account id: on Jira Cloud, JQL doesn't match users by name.
    assignee_account = resolve_assignee(jira, owned=False, owner=assignee)

    jql = build_issues_jql(
        ctx.obj.config.resolve(project, "project"),
        assignee_id=assignee_account["id"] if assignee_account else None,
        all_users=all_users,
        statuses=status or [],
        closed_statuses=ctx.obj.config.default.definition_closed,
    )

    issues: list[Issue] = jira.search_issues(
        jql,
        startAt=0,
        maxResults=ctx.obj.config.default.max_result,
        fields="key,summary,assignee,status,created",
    )

    display.display_issues(issues)

    total = getattr(issues, "total", len(issues))
    if total > len(issues):
        console.print(
            f"[yellow]Affichage de {len(issues)} ticket(s) sur {total} au total : "
            "résultat tronqué (voir max_result dans la config).[/yellow]"
        )


@app.command()
@handle_jira_errors
def projects(ctx: typer.Context) -> None:
    """List available projects.

    Example: jira get projects
    """
    jira = ctx.obj.jira_client
    project_list = jira.projects()

    display.display_tuples(columns=["Code", "Name"], rows=[(p.key, p.name) for p in project_list])


@app.command()
@handle_jira_errors
def status(
    ctx: typer.Context,
    issue_key: Annotated[
        Optional[str], typer.Argument(help="Le code du ticket. Si omis, statuts du type de ticket par défaut.")
    ] = None,
) -> None:
    """Get available statuses for the default issue type, or transitions for a specific issue.

    Example: jira get status
    Example: jira get status ST-1060
    """
    jira = ctx.obj.jira_client

    if issue_key is None:
        issue_type = ctx.obj.config.default.issue_type
        statuses_list = get_statuses_for_issue_type(jira, ctx.obj.config.default.project, issue_type)

        display.display_tuples(columns=[issue_type], rows=[(s,) for s in statuses_list])
        return

    issue: Issue = jira.issue(issue_key)
    display.display_tuples(columns=[issue.fields.issuetype.name], rows=[(t,) for t in get_transitions_from_issue(jira, issue)])


@app.command()
@handle_jira_errors
def users(
    ctx: typer.Context,
    query: Annotated[Optional[str], typer.Option(help="A string to match usernames, name or email against.")] = "%",
) -> None:
    """List users for current project.

    Default jira maxResults = 50
    Example: jira get users --query michel
    """
    jira = ctx.obj.jira_client
    users = jira.search_users(query=f"{query}")

    if not users:
        raise UserNotFoundError(str(query))

    display.display_tuples(columns=["Fullname", "account_id"], rows=[(u.displayName, u.accountId) for u in users])
