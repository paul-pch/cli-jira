from typing import TYPE_CHECKING, Annotated

import typer

from app.utils.errors import handle_jira_errors
from app.utils.exceptions import DeletionCancelledError
from app.utils.issue_fields import ISSUE_FIELDS

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Delete a specific ressource")


@app.command()
@handle_jira_errors
def issue(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(help="The code of the issue")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Ne pas demander de confirmation")] = False,
    with_subtasks: Annotated[
        bool,
        typer.Option("--with-subtasks", help="Supprimer aussi les sous-tâches, sinon Jira refuse la suppression"),
    ] = False,
) -> None:
    """Delete an issue. This cannot be undone.

    Example: jira delete issue ST-1060
    Example: jira delete issue ST-1060 --yes
    """
    jira = ctx.obj.jira_client

    issue: Issue = jira.issue(key, fields=ISSUE_FIELDS)

    # Fetched first so the confirmation names what is about to disappear, not just a key.
    if not yes and not typer.confirm(f"Supprimer définitivement {issue.key} — {issue.fields.summary} ?"):
        raise DeletionCancelledError(issue.key)

    issue.delete(deleteSubtasks=with_subtasks)

    typer.echo(f"{issue.key} supprimé.")
