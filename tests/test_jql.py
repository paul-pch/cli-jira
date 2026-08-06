from app.utils.jql import build_issues_jql, quote

CLOSED = ["Terminé", "Livré"]


def build(**overrides: object) -> str:
    defaults = {"assignee_id": None, "all_users": False, "statuses": [], "closed_statuses": CLOSED}

    return build_issues_jql(overrides.pop("project", "ST"), **{**defaults, **overrides})  # type: ignore[arg-type]


class TestQuote:
    @staticmethod
    def test_plain_value() -> None:
        assert quote("ST") == '"ST"'

    @staticmethod
    def test_double_quote_is_escaped() -> None:
        """An unescaped quote would close the literal and let the rest be read as JQL."""
        assert quote('a"b') == '"a\\"b"'

    @staticmethod
    def test_backslash_is_escaped_first() -> None:
        assert quote("a\\b") == '"a\\\\b"'


class TestBuildIssuesJql:
    @staticmethod
    def test_default_is_mine_and_not_closed() -> None:
        assert build() == (
            'project = "ST" AND assignee = currentUser() AND status not in ("Terminé", "Livré") ORDER BY updated DESC'
        )

    @staticmethod
    def test_all_users_drops_the_assignee_clause() -> None:
        assert "assignee" not in build(all_users=True)

    @staticmethod
    def test_explicit_assignee_wins_over_all_users() -> None:
        jql = build(assignee_id="acc-1", all_users=True)

        assert 'assignee = "acc-1"' in jql
        assert "currentUser()" not in jql

    @staticmethod
    def test_explicit_statuses_replace_the_closed_filter() -> None:
        """Filtering on a closed status would return nothing if both clauses were kept."""
        jql = build(statuses=["Terminé"])

        assert 'status in ("Terminé")' in jql
        assert "not in" not in jql

    @staticmethod
    def test_no_status_clause_without_closed_statuses() -> None:
        assert "status" not in build(closed_statuses=[])

    @staticmethod
    def test_project_is_quoted() -> None:
        assert build(project="ST").startswith('project = "ST"')
