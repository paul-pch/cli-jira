from unittest.mock import MagicMock

import pytest
from jira import JIRA

from app.utils.exceptions import (
    AmbiguousBoardError,
    AmbiguousSprintError,
    BoardNotFoundError,
    NoActiveSprintError,
    SprintFieldNotFoundError,
    SprintNotFoundError,
)
from app.utils.sprints import move_to_sprint, require_sprint_field, resolve_board, resolve_sprint, sprint_field
from tests.conftest import SPRINT_FIELD, make_board, make_issue, make_sprint, with_sprint_field

SPRINT_ID = 42
OTHER_SPRINT_ID = 2
BOARD_ID = 7


@pytest.fixture
def jira_client() -> MagicMock:
    sprint_field.cache_clear()
    return MagicMock(spec=JIRA)


def test_numeric_sprint_is_used_as_is(jira_client: MagicMock) -> None:
    """An id spares the two agile calls."""
    assert resolve_sprint(jira_client, "ST", None, "42") == SPRINT_ID

    jira_client.boards.assert_not_called()
    jira_client.sprints.assert_not_called()


def test_sprint_resolved_by_name(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board(board_id=7)]
    jira_client.sprints.return_value = [make_sprint(sprint_id=42, name="Sprint 10", state="future")]

    assert resolve_sprint(jira_client, "ST", None, "sprint 10") == SPRINT_ID

    jira_client.boards.assert_called_once_with(projectKeyOrID="ST", type="scrum", name=None)
    jira_client.sprints.assert_called_once_with(BOARD_ID, state="active,future")


def test_current_picks_the_active_sprint(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board()]
    jira_client.sprints.return_value = [
        make_sprint(sprint_id=1, name="Sprint 9", state="future"),
        make_sprint(sprint_id=2, name="Sprint 10", state="active"),
    ]

    assert resolve_sprint(jira_client, "ST", None, "current") == OTHER_SPRINT_ID


def test_current_without_running_sprint(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board()]
    jira_client.sprints.return_value = [make_sprint(state="future")]

    with pytest.raises(NoActiveSprintError):
        resolve_sprint(jira_client, "ST", None, "current")


def test_unknown_sprint_lists_the_open_ones(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board()]
    jira_client.sprints.return_value = [make_sprint(name="Sprint 10")]

    with pytest.raises(SprintNotFoundError, match="Sprint 10"):
        resolve_sprint(jira_client, "ST", None, "Sprint 11")


def test_ambiguous_sprint_name(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board()]
    jira_client.sprints.return_value = [make_sprint(sprint_id=1), make_sprint(sprint_id=2)]

    with pytest.raises(AmbiguousSprintError):
        resolve_sprint(jira_client, "ST", None, "Sprint 10")


def test_board_name_from_config_is_forwarded(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board(board_id=7)]

    assert resolve_board(jira_client, "ST", "ST Scrum") == BOARD_ID

    jira_client.boards.assert_called_once_with(projectKeyOrID="ST", type="scrum", name="ST Scrum")


def test_no_board(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = []

    with pytest.raises(BoardNotFoundError):
        resolve_board(jira_client, "ST", None)


def test_several_boards_ask_for_the_config_key(jira_client: MagicMock) -> None:
    jira_client.boards.return_value = [make_board(board_id=7), make_board(board_id=8, name="ST Bugs")]

    with pytest.raises(AmbiguousBoardError, match="config.toml"):
        resolve_board(jira_client, "ST", None)


def test_sprint_field_discovered_by_its_schema(jira_client: MagicMock) -> None:
    with_sprint_field(jira_client)

    assert sprint_field(jira_client) == SPRINT_FIELD


def test_sprint_field_is_looked_up_once(jira_client: MagicMock) -> None:
    """Both the fetch and the rendering ask for it, and it never changes for a given client."""
    with_sprint_field(jira_client)

    assert sprint_field(jira_client) == sprint_field(jira_client)
    jira_client.fields.assert_called_once()


def test_configured_sprint_field_skips_the_lookup(jira_client: MagicMock) -> None:
    assert sprint_field(jira_client, "customfield_99") == "customfield_99"

    jira_client.fields.assert_not_called()


def test_sprint_field_absent(jira_client: MagicMock) -> None:
    jira_client.fields.return_value = [{"id": "summary"}]

    assert sprint_field(jira_client) is None

    with pytest.raises(SprintFieldNotFoundError, match="config.toml"):
        require_sprint_field(jira_client)


def test_move_to_sprint(jira_client: MagicMock) -> None:
    move_to_sprint(jira_client, make_issue(key="ST-1"), 42)

    jira_client.add_issues_to_sprint.assert_called_once_with(42, ["ST-1"])
