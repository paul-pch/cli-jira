from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer

from app.utils import display, utils
from app.utils.errors import handle_jira_errors
from app.utils.exceptions import NothingToUpdateError
from app.utils.issue_fields import ISSUE_FIELDS, IssueFields
from app.utils.jira import transition_to_status

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Edit a specific ressource")


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
    estimate: Annotated[
        Optional[str],
        typer.Option(help="Time estimate in Jira format (e.g. 10m, 1h, 1d, 1w)"),
    ] = None,
) -> None:
    """Edit an issue.

    Example: jira edit issue ST-1060 --status 'TERMINÉ'
    Example: jira edit issue ST-1060 --description 'Nouvelle description'
    """
    if not status and not comment and not description and not description_file and not estimate:
        raise NothingToUpdateError

    jira = ctx.obj.jira_client

    issue: Issue = jira.issue(key)

    if status:
        transition_to_status(jira, issue, status)

    if description_file:
        description = utils.description_to_jira(Path(description_file).read_text(encoding="utf-8").strip())

    if fields := IssueFields(description=description, estimate=estimate).to_jira():
        issue.update(fields=fields)

    if comment:
        jira.add_comment(issue, comment)

    issue = jira.issue(key, fields=ISSUE_FIELDS)

    display.display_issue(issue)
