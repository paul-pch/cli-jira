from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer

from app.utils import display, utils
from app.utils.errors import handle_jira_errors
from app.utils.issue_fields import ISSUE_FIELDS, IssueFields
from app.utils.jira import resolve_assignee, transition_to_status

if TYPE_CHECKING:
    from jira import Issue

app = typer.Typer(help="Create a specific ressource")


@app.command()
@handle_jira_errors
def issue(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Title")],
    description: Annotated[Optional[str], typer.Option(help="Larger description")] = "",
    description_file: Annotated[Optional[str], typer.Option(help="File containing the description")] = None,
    issuetype: Annotated[Optional[str], typer.Option(help="Caterogy of the issue. Default in config.toml")] = None,
    project: Annotated[
        Optional[str],
        typer.Option(help="Code of the project to which the ticket is attached. Default in config.toml"),
    ] = None,
    labels: Annotated[
        Optional[list[str]],
        typer.Option(help="Labels assigned to the issue. Default value in config.toml"),
    ] = None,
    owned: Annotated[
        Optional[bool],
        typer.Option(help="Presise if the issue is owned by the current author"),
    ] = True,
    owner: Annotated[
        Optional[str],
        typer.Option(help="The onwer of the issue (override --owned)"),
    ] = None,
    parent: Annotated[
        Optional[str],
        typer.Option(help="Key of the parent issue (e.g., PROJ-123)"),
    ] = None,
    estimate: Annotated[
        Optional[str],
        typer.Option(help="Time estimate in Jira format (e.g. 10m, 1h, 1d, 1w)"),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option(help="Status to move the issue to right after creation. Example : 'EN COURS'"),
    ] = None,
) -> None:
    """Create an issue.

    Example: jira create issue <title> --labels <text>
    Example: jira create issue <title> --status 'EN COURS'
    """
    jira = ctx.obj.jira_client

    config = ctx.obj.config

    if description_file:
        description = utils.description_to_jira(Path(description_file).read_text(encoding="utf-8").strip())

    issuetype = config.resolve(issuetype, "issue_type")
    project = config.resolve(project, "project")

    if not labels:
        labels = []

    labels += config.default.labels

    fields = IssueFields(
        project=project,
        summary=title,
        description=description,
        issuetype=issuetype,
        labels=labels,
        parent=parent,
        estimate=estimate,
        assignee=resolve_assignee(jira, owned=bool(owned), owner=owner),
    )

    new_issue: Issue = jira.create_issue(fields=fields.to_jira())

    if status:
        transition_to_status(jira, new_issue, status)
        new_issue = jira.issue(new_issue.key, fields=ISSUE_FIELDS)

    display.display_issue(new_issue)
