import typer
from rich.console import Console
from rich.table import Table

from .config import JIRA_PROJECT

app = typer.Typer(help="Manage projects")
console = Console()


@app.command()
def project(ctx: typer.Context) -> None:
    try:
        jira = ctx.obj
        projects = jira.projects()
        table = Table("Code", "Nom")
        for project in projects:
            table.add_row(project.key, project.name)

        console.print(table)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def ticket(ctx: typer.Context) -> None:
    try:
        jira = ctx.obj

        jql = f"project = {JIRA_PROJECT} AND status NOT IN (Closed, Resolved) ORDER BY created DESC"

        issues = jira.search_issues(jql_str=jql, startAt=0, maxResults=10, fields="key,summary,assignee,status,created")

        table = Table("Code", "Nom", "Statut", "Responsable")
        for issue in issues:
            table.add_row(
                issue.key, issue.fields.summary, issue.fields.status.name, getattr(issue.fields.assignee, "displayName", "None")
            )

        console.print(table)
    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
