from typing import TYPE_CHECKING, Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from app.utils.jira_utils import get_transitions_from_issue
from app.utils.utils import display_issues, display_transitions

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Get a specific ressource")
console = Console()


@app.command()
def issue(ctx: typer.Context, issue_key: Annotated[str, typer.Argument(help="The code of the issue")]) -> None:
    """Get a specific issue.

    Example: jira get issue ST-1060
    """
    try:
        jira = ctx.obj.jira_client

        issue: Issue = jira.issue(issue_key, fields="key,summary,assignee,status,created")

        display_issues([issue])

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def issues(ctx: typer.Context) -> None:
    """List owned issues.

    Example: jira list issues
    """
    try:
        jira = ctx.obj.jira_client

        closed_statuses = ctx.obj.config["default"]["definition_closed"]
        status_closed_list_str = ", ".join(f'"{s}"' for s in closed_statuses)

        jql = f"assignee = currentUser() AND status not in ({status_closed_list_str}) ORDER BY updated DESC"

        issues: list[Issue] = jira.search_issues(
            jql,
            startAt=0,
            maxResults=ctx.obj.config["default"]["max_result"],
            fields="key,summary,assignee,status,created",
        )

        display_issues(issues)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def project(ctx: typer.Context) -> None:
    """List available projects.

    Example: jira list project
    """
    try:
        jira = ctx.obj.jira_client
        projects = jira.projects()
        table = Table("Code", "Nom")
        for project in projects:
            table.add_row(project.key, project.name)

        console.print(table)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def status(ctx: typer.Context, issue_key: Annotated[str, typer.Argument(help="The code of the issue")]) -> None:
    """Get available transitions for a specific issue.

    Example: jira get status ST-1060
    """
    jira = ctx.obj.jira_client
    issue: Issue = jira.issue(issue_key)
    display_transitions(get_transitions_from_issue(ctx, issue), issue.fields.issuetype.name)


@app.command()
def users(
    ctx: typer.Context,
    query: Annotated[Optional[str], typer.Option(help="A string to match usernames, name or email against.")] = "%",
) -> None:
    """List users for current project.

    Default jira maxResults = 50
    Example: jira get users --query michel
    """
    try:
        jira = ctx.obj.jira_client
        users = jira.search_users(query=f"{query}")

        if not users:
            console.print("No user found.", style="yellow")
            raise typer.Exit(code=1)

        table = Table("Fullname", "account_id")
        for u in users:
            table.add_row(u.displayName, u.accountId)
        console.print(table)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
