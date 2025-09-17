from typing import Annotated

import typer
from rich.console import Console

from app.utils.utils import print_issue

app = typer.Typer(help="Get a specific ressource")
console = Console()


@app.command()
def issue(ctx: typer.Context, issue_key: Annotated[str, typer.Argument(help="The code of the issue")]) -> None:
    """Get a specific issue."""
    try:
        jira = ctx.obj.jira_client

        issue = jira.issue(issue_key, fields="key,summary,assignee,status,created")

        print_issue(issue)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
