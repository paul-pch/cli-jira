from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer

from app.utils import display, utils
from app.utils.errors import handle_jira_errors
from app.utils.exceptions import NothingToUpdateError
from app.utils.issue_fields import ISSUE_FIELDS, IssueFields, label_operations
from app.utils.jira import transition_to_status

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Edit a specific ressource")


@app.command()
@handle_jira_errors
def issue(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(help="Title")],
    title: Annotated[Optional[str], typer.Option(help="New title (summary) to set")] = None,
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
    labels: Annotated[
        Optional[list[str]],
        typer.Option(help="Label to add, keeping the existing ones. Repeatable."),
    ] = None,
    remove_labels: Annotated[
        Optional[list[str]],
        typer.Option(help="Label to remove, keeping the other ones. Repeatable."),
    ] = None,
) -> None:
    """Edit an issue.

    Example: jira edit issue ST-1060 --status 'TERMINÉ'
    Example: jira edit issue ST-1060 --title 'Nouveau titre'
    Example: jira edit issue ST-1060 --description 'Nouvelle description'
    Example: jira edit issue ST-1060 --labels OPS --labels Cycle11 --remove-labels Cycle10
    """
    if not any([title, status, comment, description, description_file, estimate, labels, remove_labels]):
        raise NothingToUpdateError

    jira = ctx.obj.jira_client

    issue: Issue = jira.issue(key)

    if status:
        transition_to_status(jira, issue, status)

    if description_file:
        description = utils.description_to_jira(Path(description_file).read_text(encoding="utf-8").strip())

    fields = IssueFields(summary=title, description=description, estimate=estimate).to_jira()
    operations = label_operations(labels or [], remove_labels or [])

    if fields or operations:
        issue.update(fields=fields, update=operations)

    if comment:
        jira.add_comment(issue, comment)

    issue = jira.issue(key, fields=ISSUE_FIELDS)

    display.display_issue(issue)
