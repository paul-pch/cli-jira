from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer
from rich.console import Console

from app.utils import display, utils
from app.utils.errors import handle_jira_errors
from app.utils.exceptions import InvalidJiraStatusError

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Edit a specific ressource")
console = Console()


@app.command()
@handle_jira_errors
def issue(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(help="Title")],
    status: Annotated[
        Optional[str],
        typer.Option(help="New status to update. Example : 'EN COURS DE REVUE'"),
    ] = None,
    comment: Annotated[Optional[str], typer.Option(help="Comment to add")] = None,
    description: Annotated[Optional[str], typer.Option(help="New description to set")] = None,
    description_file: Annotated[Optional[str], typer.Option(help="File containing the new description")] = None,
) -> None:
    """Edit an issue.

    Example: jira edit issue ST-1060 --status 'TERMINÉ'
    Example: jira edit issue ST-1060 --description 'Nouvelle description'
    """
    if not status and not comment and not description and not description_file:
        console.print("Nothing to update !", style="yellow")
        raise typer.Exit(code=1)

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

    if description_file:
        description = utils.description_to_jira(Path(description_file).read_text(encoding="utf-8").strip())
    if description:
        issue.update(description=description)

    if comment:
        jira.add_comment(issue, comment)

    issue = jira.issue(key, fields="key,description,summary,issuetype,assignee,status,created,labels")

    display.display_issue(issue)
