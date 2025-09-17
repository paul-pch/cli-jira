from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

from app.utils.utils import display_issues

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="List the ressources availables for the current user")
console = Console()


@app.command()
def project(ctx: typer.Context) -> None:
    """List available projects."""
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
def issues(ctx: typer.Context) -> None:
    """List owned issues."""
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
