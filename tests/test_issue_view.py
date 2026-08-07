from types import SimpleNamespace

from app.utils.issue_view import UNASSIGNED, UNKNOWN_AUTHOR, IssueView
from tests.conftest import SPRINT_FIELD, make_comment, make_issue, make_issue_link


class TestSprint:
    @staticmethod
    def test_read_from_an_api_object() -> None:
        issue = make_issue(sprint=[SimpleNamespace(id=42, name="Sprint 10", state="active")])

        assert IssueView.from_issue(issue, SPRINT_FIELD).sprint == "Sprint 10"

    @staticmethod
    def test_read_from_a_dict() -> None:
        issue = make_issue(sprint=[{"id": 42, "name": "Sprint 10"}])

        assert IssueView.from_issue(issue, SPRINT_FIELD).sprint == "Sprint 10"

    @staticmethod
    def test_read_from_the_server_string_dump() -> None:
        """Jira Server hands back the toString() of its Java object instead of a structure."""
        raw = "com.atlassian.greenhopper.service.sprint.Sprint@1[id=42,name=Sprint 10,state=ACTIVE,rapidViewId=7]"
        issue = make_issue(sprint=[raw])

        assert IssueView.from_issue(issue, SPRINT_FIELD).sprint == "Sprint 10"

    @staticmethod
    def test_last_sprint_wins() -> None:
        """The field keeps every sprint the issue went through, in order."""
        issue = make_issue(
            sprint=[
                SimpleNamespace(name="Sprint 9", state="closed"),
                SimpleNamespace(name="Sprint 10", state="active"),
            ],
        )

        assert IssueView.from_issue(issue, SPRINT_FIELD).sprint == "Sprint 10"

    @staticmethod
    def test_issue_outside_any_sprint() -> None:
        assert IssueView.from_issue(make_issue(sprint=[]), SPRINT_FIELD).sprint is None

    @staticmethod
    def test_no_sprint_field_on_the_instance() -> None:
        issue = make_issue(sprint=[SimpleNamespace(name="Sprint 10")])

        assert IssueView.from_issue(issue).sprint is None


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
    def test_time_spent_and_remaining() -> None:
        view = IssueView.from_issue(
            make_issue(timetracking={"originalEstimate": "1d", "timeSpent": "2h", "remainingEstimate": "6h"}),
        )

        assert view.time_spent == "2h"
        assert view.remaining_estimate == "6h"

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


class TestIssueViewLinks:
    @staticmethod
    def test_no_link() -> None:
        assert IssueView.from_issue(make_issue()).links == []

    @staticmethod
    def test_outward_link_reads_the_outward_wording() -> None:
        issue = make_issue(issuelinks=[make_issue_link(relation="blocks", other_key="ST-2")])

        assert IssueView.from_issue(issue).links == [("blocks", "ST-2")]

    @staticmethod
    def test_inward_link_reads_the_inward_wording() -> None:
        issue = make_issue(issuelinks=[make_issue_link(relation="is blocked by", other_key="ST-3", outward=False)])

        assert IssueView.from_issue(issue).links == [("is blocked by", "ST-3")]


class TestIssueViewComments:
    @staticmethod
    def test_no_comment() -> None:
        assert IssueView.from_issue(make_issue()).comments == []

    @staticmethod
    def test_comments_are_flattened_from_the_nested_field() -> None:
        issue = make_issue(comments=[make_comment(author="Jean Dupont", body="Bonjour")])

        comment = IssueView.from_issue(issue).comments[0]

        assert comment.author == "Jean Dupont"
        assert comment.body == "Bonjour"
        assert comment.created == "2024-01-02"

    @staticmethod
    def test_comment_without_author() -> None:
        issue = make_issue(comments=[make_comment(author=None)])

        assert IssueView.from_issue(issue).comments[0].author == UNKNOWN_AUTHOR

    @staticmethod
    def test_order_is_preserved() -> None:
        issue = make_issue(comments=[make_comment(body="Premier"), make_comment(body="Second")])

        assert [c.body for c in IssueView.from_issue(issue).comments] == ["Premier", "Second"]
