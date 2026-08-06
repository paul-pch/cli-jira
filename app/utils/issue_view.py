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


def _links(issuelinks: Any) -> list[tuple[str, str]]:  # noqa: ANN401
    """Flatten issue links into (relation as read from this issue, other issue key) pairs.

    Jira puts the other issue under `outwardIssue` or `inwardIssue` depending on which
    end of the relation the current issue sits on, and words the relation accordingly.
    """
    relations = []

    for link in issuelinks or []:
        outward = getattr(link, "outwardIssue", None)
        inward = getattr(link, "inwardIssue", None)

        if outward is not None:
            relations.append((link.type.outward, outward.key))
        elif inward is not None:
            relations.append((link.type.inward, inward.key))

    return relations


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
    links: list[tuple[str, str]]

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
            links=_links(getattr(fields, "issuelinks", None)),
        )
