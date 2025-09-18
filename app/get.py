from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console

from app.utils.utils import display_issues

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
