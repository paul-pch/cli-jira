from typing import TYPE_CHECKING, Annotated, Optional

import typer
from rich.console import Console

from app.utils import display
from app.utils.errors import handle_jira_errors
from app.utils.exceptions import ConflictingJqlOptionsError, UserNotFoundError
from app.utils.issue_fields import issue_fields
from app.utils.jira import get_statuses_for_issue_type, get_transitions_from_issue, resolve_assignee
from app.utils.jql import build_issues_jql
from app.utils.sprints import OPEN_STATES, resolve_board, resolve_sprint, sprint_field

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
    field = sprint_field(jira, ctx.obj.config.default.sprint_field)

    issue: Issue = jira.issue(issue_key, fields=issue_fields(field))
    remote_links = jira.remote_links(issue_key)

    display.display_issue(issue, remote_links, sprint_field=field)


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
    jql: Annotated[
        Optional[str],
        typer.Option(help="Requête JQL brute, utilisée telle quelle. Exclut les autres options de filtre."),
    ] = None,
    limit: Annotated[
        Optional[int],
        typer.Option(help="Nombre maximum de tickets à afficher. Par défaut max_result de config.toml."),
    ] = None,
    start: Annotated[int, typer.Option(help="Index du premier ticket à afficher (pagination).")] = 0,
    sprint: Annotated[
        Optional[str],
        typer.Option(help="Ne garder que les tickets de ce sprint : son nom, son id, ou 'current'."),
    ] = None,
) -> None:
    """List issues.

    Example: jira get issues
    Example: jira get issues --all
    Example: jira get issues --project ST --status 'EN COURS'
    Example: jira get issues --assignee michel
    Example: jira get issues --sprint current
    Example: jira get issues --jql 'project = ST AND labels = OPS ORDER BY created DESC'
    Example: jira get issues --limit 10 --start 10
    """
    if jql and any([project, status, assignee, all_users, sprint]):
        raise ConflictingJqlOptionsError

    jira = ctx.obj.jira_client

    if not jql:
        # Resolved to an account id: on Jira Cloud, JQL doesn't match users by name.
        assignee_account = resolve_assignee(jira, owned=False, owner=assignee)
        project = ctx.obj.config.resolve(project, "project")

        jql = build_issues_jql(
            project,
            assignee_id=assignee_account["id"] if assignee_account else None,
            all_users=all_users,
            statuses=status or [],
            closed_statuses=ctx.obj.config.default.definition_closed,
            sprint_id=resolve_sprint(jira, project, ctx.obj.config.default.board, sprint) if sprint else None,
        )

    issues: list[Issue] = jira.search_issues(
        jql,
        startAt=start,
        maxResults=ctx.obj.config.resolve(limit, "max_result"),
        fields="key,summary,assignee,status,created",
    )

    display.display_issues(issues)

    total = getattr(issues, "total", len(issues))

    if not issues:
        console.print(f"[yellow]Aucun ticket à partir de l'index {start} (total : {total}).[/yellow]")
    elif start + len(issues) < total:
        console.print(
            f"[yellow]Tickets {start + 1}-{start + len(issues)} sur {total}. Suite : --start {start + len(issues)}[/yellow]"
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
    issue_type: Annotated[
        Optional[str],
        typer.Option(help="Type de ticket dont lister les statuts. Par défaut celui de config.toml."),
    ] = None,
    project: Annotated[
        Optional[str],
        typer.Option(help="Code du projet. Par défaut celui de config.toml."),
    ] = None,
) -> None:
    """Get available statuses for an issue type, or transitions for a specific issue.

    Example: jira get status
    Example: jira get status ST-1060
    Example: jira get status --issue-type Bug
    """
    jira = ctx.obj.jira_client

    if issue_key is None:
        issue_type = ctx.obj.config.resolve(issue_type, "issue_type")
        statuses_list = get_statuses_for_issue_type(jira, ctx.obj.config.resolve(project, "project"), issue_type)

        display.display_tuples(columns=[issue_type], rows=[(s,) for s in statuses_list])
        return

    issue: Issue = jira.issue(issue_key)
    display.display_tuples(columns=[issue.fields.issuetype.name], rows=[(t,) for t in get_transitions_from_issue(jira, issue)])


@app.command()
@handle_jira_errors
def sprints(
    ctx: typer.Context,
    project: Annotated[
        Optional[str],
        typer.Option(help="Code du projet. Par défaut celui de config.toml."),
    ] = None,
    board: Annotated[
        Optional[str],
        typer.Option(help="Nom du tableau scrum. Par défaut celui de config.toml, sinon le seul du projet."),
    ] = None,
    state: Annotated[
        str,
        typer.Option(help="États à lister, séparés par des virgules : active, future, closed."),
    ] = OPEN_STATES,
) -> None:
    """List the sprints of the project's scrum board.

    Example: jira get sprints
    Example: jira get sprints --state closed
    """
    jira = ctx.obj.jira_client
    project = ctx.obj.config.resolve(project, "project")

    board_id = resolve_board(jira, project, ctx.obj.config.resolve(board, "board"))

    display.display_tuples(
        columns=["Id", "Nom", "État"],
        rows=[(str(s.id), s.name, s.state) for s in jira.sprints(board_id, state=state)],
    )


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
