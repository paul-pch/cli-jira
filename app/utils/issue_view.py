from dataclasses import dataclass
from typing import Any

from jira import Issue

UNASSIGNED = "Non assigné"


def _timetracking(timetracking: Any, *keys: str) -> str | None:  # noqa: ANN401
    """Read the first of `keys` present in the timetracking field, whatever shape Jira returned it in.

    The API hands back an object, while a plain dict is what gets written.
    """
    if not timetracking:
        return None

    for key in keys:
        value = timetracking.get(key) if isinstance(timetracking, dict) else getattr(timetracking, key, None)
        if value:
            return value

    return None


@dataclass(frozen=True, slots=True)
class IssueView:
    """An issue reduced to what the console shows, with every optional field resolved once."""

    key: str
    summary: str
    issuetype: str
    status: str
    assignee: str
    labels: list[str]
    created: str
    description: str | None
    estimate: str | None
    time_spent: str | None
    remaining_estimate: str | None

    @classmethod
    def from_issue(cls, issue: Issue) -> "IssueView":
        fields = issue.fields
        assignee = getattr(fields, "assignee", None)
        created = getattr(fields, "created", None) or ""
        timetracking = getattr(fields, "timetracking", None)

        return cls(
            key=issue.key,
            summary=getattr(fields, "summary", "") or "",
            issuetype=getattr(fields.issuetype, "name", "") if getattr(fields, "issuetype", None) else "",
            status=getattr(fields.status, "name", "") if getattr(fields, "status", None) else "",
            assignee=getattr(assignee, "displayName", UNASSIGNED) if assignee else UNASSIGNED,
            labels=list(getattr(fields, "labels", None) or []),
            created=created[:10],
            description=getattr(fields, "description", None),
            estimate=_timetracking(timetracking, "originalEstimate", "estimate"),
            time_spent=_timetracking(timetracking, "timeSpent"),
            remaining_estimate=_timetracking(timetracking, "remainingEstimate"),
        )
