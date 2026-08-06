from app.utils.issue_fields import IssueFields


class TestIssueFields:
    @staticmethod
    def test_empty_payload_when_nothing_is_set() -> None:
        assert IssueFields().to_jira() == {}

    @staticmethod
    def test_wraps_values_in_the_jira_shapes() -> None:
        payload = IssueFields(
            project="ST",
            summary="Titre",
            issuetype="Story Technique",
            parent="ST-1",
            estimate="2h",
            assignee={"id": "acc-me"},
        ).to_jira()

        assert payload == {
            "project": {"key": "ST"},
            "summary": "Titre",
            "issuetype": {"name": "Story Technique"},
            "parent": {"key": "ST-1"},
            "timetracking": {"estimate": "2h"},
            "assignee": {"id": "acc-me"},
        }

    @staticmethod
    def test_partial_update_omits_untouched_fields() -> None:
        assert IssueFields(description="Nouvelle description").to_jira() == {"description": "Nouvelle description"}

    @staticmethod
    def test_empty_but_explicit_values_are_kept() -> None:
        """An empty description or label list is a deliberate reset, not an absent field."""
        assert IssueFields(description="", labels=[]).to_jira() == {"description": "", "labels": []}
