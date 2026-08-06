from dataclasses import dataclass
from typing import Any

# Fields requested from Jira whenever a single issue is fetched for display.
# Keep it in sync with what `display.py` reads.
ISSUE_FIELDS = "key,description,summary,issuetype,assignee,status,created,labels,timetracking"


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
