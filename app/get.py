from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Get a specific ressource")
console = Console()


@app.command()
def issue(ctx: typer.Context, issue_key: Annotated[str, typer.Argument(help="The code of the issue")]) -> None:
    """
    Get a specific issue
    """
    try:
        jira = ctx.obj.jira_client

        issue = jira.issue(issue_key, fields="key,summary,assignee,status,created")

        table = Table("Code", "Nom", "Statut", "Responsable")
        table.add_row(
            issue.key,
            issue.fields.summary,
            issue.fields.status.name,
            getattr(issue.fields.assignee, "displayName", "None"),
        )

        console.print(table)
    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
