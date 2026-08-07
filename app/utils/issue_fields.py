from dataclasses import dataclass
from typing import Any

# Fields requested from Jira whenever a single issue is fetched for display.
# Keep it in sync with what `display.py` reads.
ISSUE_FIELDS = "key,description,summary,issuetype,assignee,status,created,labels,timetracking,issuelinks,comment"


def issue_fields(sprint_field: str | None = None) -> str:
    """Fields to request for display, the sprint one added once its id is known.

    The sprint lives in a custom field whose id changes per Jira instance, so it cannot sit
    in the constant above.
    """
    return f"{ISSUE_FIELDS},{sprint_field}" if sprint_field else ISSUE_FIELDS


def label_operations(add: list[str], remove: list[str]) -> dict[str, list[dict[str, str]]]:
    """Build the `update` verb payload for a partial label edit.

    Jira applies these server-side, so no read-modify-write and no lost update when
    someone else touches the labels at the same time.
    """
    operations = [{"add": label} for label in add] + [{"remove": label} for label in remove]

    return {"labels": operations} if operations else {}


@dataclass(slots=True)
class IssueFields:
    """Builder for the `fields` payload shared by `create` and `edit`.

    Every attribute left at None is omitted from the payload, so the same object
    describes a full creation and a partial update.
    """

    project: str | None = None
    summary: str | None = None
    description: str | None = None
    issuetype: str | None = None
    labels: list[str] | None = None
    parent: str | None = None
    estimate: str | None = None
    assignee: dict[str, str] | None = None

    def to_jira(self) -> dict[str, Any]:
        """Render the Jira payload, wrapping each value in the shape Jira expects."""
        payload: dict[str, Any] = {}

        if self.project is not None:
            payload["project"] = {"key": self.project}
        if self.summary is not None:
            payload["summary"] = self.summary
        if self.description is not None:
            payload["description"] = self.description
        if self.issuetype is not None:
            payload["issuetype"] = {"name": self.issuetype}
        if self.labels is not None:
            payload["labels"] = self.labels
        if self.parent is not None:
            payload["parent"] = {"key": self.parent}
        if self.estimate is not None:
            payload["timetracking"] = {"estimate": self.estimate}
        if self.assignee is not None:
            payload["assignee"] = self.assignee

        return payload
