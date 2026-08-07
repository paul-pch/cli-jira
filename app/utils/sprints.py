from typing import TYPE_CHECKING

from jira import JIRA, Issue

from app.utils.exceptions import (
    AmbiguousBoardError,
    AmbiguousSprintError,
    BoardNotFoundError,
    NoActiveSprintError,
    SprintNotFoundError,
)

if TYPE_CHECKING:
    from jira.resources import Sprint

# Keyword accepted by --sprint, and the value used when nothing is asked for.
CURRENT = "current"

# A closed sprint accepts no issue, so it is never a resolution candidate.
OPEN_STATES = "active,future"


def resolve_board(jira: JIRA, project: str, board: str | None) -> int:
    """Find the scrum board carrying the sprints of a project."""
    boards = jira.boards(projectKeyOrID=project, type="scrum", name=board)

    if not boards:
        raise BoardNotFoundError(project, board)

    if len(boards) > 1:
        raise AmbiguousBoardError(project, [b.name for b in boards])

    return int(boards[0].id)


def resolve_sprint(jira: JIRA, project: str, board: str | None, wanted: str = CURRENT) -> int:
    """Resolve a `--sprint` value to a sprint id.

    Accepts a numeric id (used as-is, no lookup), the `current` keyword for the single
    active sprint, or a sprint name matched case-insensitively among the open sprints.
    """
    if wanted.isdigit():
        return int(wanted)

    sprints: list[Sprint] = jira.sprints(resolve_board(jira, project, board), state=OPEN_STATES)

    if wanted.lower() == CURRENT:
        matching = [s for s in sprints if s.state.lower() == "active"]
        if not matching:
            raise NoActiveSprintError(project)
    else:
        matching = [s for s in sprints if s.name.lower() == wanted.lower()]
        if not matching:
            raise SprintNotFoundError(wanted, [s.name for s in sprints])

    if len(matching) > 1:
        raise AmbiguousSprintError(wanted, [s.name for s in matching])

    return int(matching[0].id)


def move_to_sprint(jira: JIRA, issue: Issue, sprint_id: int) -> None:
    """Move an issue into a sprint.

    The agile endpoint is used rather than the sprint custom field: its id changes from one
    Jira instance to the next. Jira removes the issue from its previous sprint by itself.
    """
    jira.add_issues_to_sprint(sprint_id, [issue.key])
