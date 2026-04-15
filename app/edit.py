from typing import TYPE_CHECKING, Annotated, Optional

import typer
from rich.console import Console

from app.utils import display
from app.utils.exceptions import InvalidJiraStatusError

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Edit a specific ressource")
console = Console()


@app.command()
def issue(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(help="Title")],
    status: Annotated[
        Optional[str],
        typer.Option(help="New status to update. Example : 'EN COURS DE REVUE'"),
    ] = None,
    comment: Annotated[Optional[str], typer.Option(help="Comment to add")] = None,
) -> None:
    """Edit an issue.

    Example: jira edit issue ST-1060 --status 'TERMINÉ'
    """
    if not status and not comment:
        console.print("Nothing to update !", style="yellow")
        raise typer.Exit(code=1)
    try:
        jira = ctx.obj.jira_client

        issue: Issue = jira.issue(key)

        if status:
            transitions = jira.transitions(issue)
            transition_id = None
            for t in transitions:
                if t["name"].lower() == status.lower():
                    transition_id = t["id"]
                    break
            if not transition_id:
                raise InvalidJiraStatusError(status)
            jira.transition_issue(issue, transition_id)

        issue = jira.issue(key, fields="key,description,summary,issuetype,assignee,status,created,labels")

        if comment:
            jira.add_comment(issue, comment)

        display.display_issue(issue)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
