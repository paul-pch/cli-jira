from types import SimpleNamespace

from app.utils.issue_view import UNASSIGNED, IssueView
from tests.conftest import make_issue


class TestIssueView:
    @staticmethod
    def test_reads_the_nested_names() -> None:
        view = IssueView.from_issue(make_issue(key="ST-1", summary="Titre", status="En cours"))

        assert view.key == "ST-1"
        assert view.summary == "Titre"
        assert view.status == "En cours"
        assert view.issuetype == "Story Technique"
        assert view.assignee == "Jean Dupont"

    @staticmethod
    def test_created_is_trimmed_to_the_date() -> None:
        view = IssueView.from_issue(make_issue(created="2024-01-01T00:00:00.000+0000"))

        assert view.created == "2024-01-01"

    @staticmethod
    def test_unassigned_issue() -> None:
        view = IssueView.from_issue(make_issue(assignee_name=None))

        assert view.assignee == UNASSIGNED

    @staticmethod
    def test_estimate_from_the_api_object() -> None:
        view = IssueView.from_issue(make_issue(timetracking=SimpleNamespace(originalEstimate="3h")))

        assert view.estimate == "3h"

    @staticmethod
    def test_estimate_from_a_plain_dict() -> None:
        view = IssueView.from_issue(make_issue(timetracking={"originalEstimate": "3h"}))

        assert view.estimate == "3h"

    @staticmethod
    def test_no_estimate() -> None:
        assert IssueView.from_issue(make_issue()).estimate is None

    @staticmethod
    def test_missing_optional_fields_do_not_crash() -> None:
        """Jira omits fields that were never set, and `--fields` narrows the payload further."""
        bare = SimpleNamespace(
            key="ST-1",
            fields=SimpleNamespace(
                summary="Titre",
                issuetype=SimpleNamespace(name="Bug"),
                status=SimpleNamespace(name="Ouvert"),
            ),
        )

        view = IssueView.from_issue(bare)

        assert view.assignee == UNASSIGNED
        assert view.labels == []
        assert view.created == ""
        assert view.description is None
        assert view.estimate is None
