from typing import TYPE_CHECKING, Annotated, Any, Optional

import typer
from rich.console import Console

from app.utils.utils import display_issues

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Create a specific ressource")
console = Console()


@app.command()
def issue(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Title")],
    description: Annotated[Optional[str], typer.Option(help="Larger description")] = "",
    issuetype: Annotated[Optional[str], typer.Option(help="Caterogy of the issue. Default in config.toml")] = None,
    project: Annotated[
        Optional[str],
        typer.Option(help="Code of the project to which the ticket is attached. Default in config.toml"),
    ] = None,
    labels: Annotated[
        Optional[list[str]],
        typer.Option(help="Labels assigned to the issue. Default value in config.toml"),
    ] = None,
) -> None:
    """Create an issue.

    Example: jira create issue <title> --labels <text>
    """
    try:
        jira = ctx.obj.jira_client

        if not issuetype:
            issuetype = ctx.obj.config["default"]["issue_type"]

        if not labels:
            labels = []

        labels += ctx.obj.config["default"]["labels"]

        if not project:
            project = ctx.obj.config["default"]["project"]

        # Compte lié au token jira
        account_id = jira.myself()["accountId"]

        fields: dict[str, Any] = {
            "project": {"key": project},
            "summary": title,
            "description": description,
            "issuetype": {"name": issuetype},
            "labels": labels,
            "assignee": {"id": account_id},
        }

        new_issue: Issue = jira.create_issue(fields=fields)
        display_issues([new_issue])

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
