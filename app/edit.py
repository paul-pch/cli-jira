from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer

from app.utils import display, utils
from app.utils.errors import handle_jira_errors
from app.utils.exceptions import ConflictingParentOptionsError, ConflictingSprintOptionsError, NothingToUpdateError
from app.utils.issue_fields import IssueFields, issue_fields, label_operations
from app.utils.jira import link_issues, resolve_assignee, transition_to_status
from app.utils.sprints import move_to_sprint, require_sprint_field, resolve_sprint, sprint_field

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
    worklog: Annotated[
        Optional[str],
        typer.Option(help="Time actually spent, logged as a worklog entry (e.g. 10m, 1h, 1d, 1w)"),
    ] = None,
    labels: Annotated[
        Optional[list[str]],
        typer.Option(help="Label to add, keeping the existing ones. Repeatable."),
    ] = None,
    remove_labels: Annotated[
        Optional[list[str]],
        typer.Option(help="Label to remove, keeping the other ones. Repeatable."),
    ] = None,
    owned: Annotated[bool, typer.Option("--owned", help="Reassign the issue to the current author")] = False,
    owner: Annotated[
        Optional[str],
        typer.Option(help="New owner of the issue (override --owned)"),
    ] = None,
    parent: Annotated[
        Optional[str],
        typer.Option(help="Key of the parent issue to attach to (e.g., PROJ-123)"),
    ] = None,
    no_parent: Annotated[bool, typer.Option("--no-parent", help="Detach the issue from its parent")] = False,
    link_issue: Annotated[
        Optional[list[str]],
        typer.Option(help="Key of an issue to link to (e.g., PROJ-123). Repeatable."),
    ] = None,
    link_type: Annotated[
        str,
        typer.Option(help="Relation carried by --link-issue, read from this issue. Example : 'blocks'"),
    ] = "Relates",
    sprint: Annotated[
        Optional[str],
        typer.Option(help="Sprint où déplacer le ticket : son nom, son id, ou 'current' pour le sprint actif."),
    ] = None,
    no_sprint: Annotated[bool, typer.Option("--no-sprint", help="Sortir le ticket de son sprint, vers le backlog")] = False,
) -> None:
    """Edit an issue.

    Example: jira edit issue ST-1060 --status 'TERMINÉ'
    Example: jira edit issue ST-1060 --title 'Nouveau titre'
    Example: jira edit issue ST-1060 --description 'Nouvelle description'
    Example: jira edit issue ST-1060 --labels OPS --labels Cycle11 --remove-labels Cycle10
    Example: jira edit issue ST-1060 --owner michel
    Example: jira edit issue ST-1060 --parent ST-XXXX
    Example: jira edit issue ST-1060 --worklog 2h
    Example: jira edit issue ST-1060 --link-type blocks --link-issue ST-1061
    Example: jira edit issue ST-1060 --sprint current
    Example: jira edit issue ST-1060 --no-sprint
    """
    changes = [
        title,
        status,
        comment,
        description,
        description_file,
        estimate,
        worklog,
        labels,
        remove_labels,
        owned,
        owner,
        sprint,
    ]

    if not any([*changes, parent, no_parent, link_issue, no_sprint]):
        raise NothingToUpdateError

    if parent and no_parent:
        raise ConflictingParentOptionsError

    if sprint and no_sprint:
        raise ConflictingSprintOptionsError

    jira = ctx.obj.jira_client

    issue: Issue = jira.issue(key)

    assignee = resolve_assignee(jira, owned=owned, owner=owner)

    if status:
        transition_to_status(jira, issue, status)

    if description_file:
        description = utils.description_to_jira(Path(description_file).read_text(encoding="utf-8").strip())

    fields = IssueFields(
        summary=title,
        description=description,
        estimate=estimate,
        assignee=assignee,
        parent=parent,
    ).to_jira()

    # IssueFields uses None to mean "leave untouched", so the explicit null Jira wants
    # for a detach is set here rather than through the builder.
    if no_parent:
        fields["parent"] = None

    # The agile API only adds to a sprint; leaving one means nulling the custom field.
    if no_sprint:
        fields[require_sprint_field(jira, ctx.obj.config.default.sprint_field)] = None

    operations = label_operations(labels or [], remove_labels or [])

    if fields or operations:
        issue.update(fields=fields, update=operations)

    if comment:
        jira.add_comment(issue, comment)

    # A worklog is its own resource, not a field: Jira recomputes the remaining estimate from it.
    if worklog:
        jira.add_worklog(issue, timeSpent=worklog)

    if link_issue:
        link_issues(jira, issue, link_type, link_issue)

    if sprint:
        # The project comes from the issue, not from the config: an edit may target another one.
        project = getattr(getattr(issue.fields, "project", None), "key", None) or ctx.obj.config.default.project
        move_to_sprint(jira, issue, resolve_sprint(jira, project, ctx.obj.config.default.board, sprint))

    field = sprint_field(jira, ctx.obj.config.default.sprint_field)
    issue = jira.issue(key, fields=issue_fields(field))

    display.display_issue(issue, sprint_field=field)
