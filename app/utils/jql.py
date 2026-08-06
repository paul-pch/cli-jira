ORDERING = "ORDER BY updated DESC"


def quote(value: str) -> str:
    """Quote a JQL literal, escaping what would otherwise close the string early."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')

    return f'"{escaped}"'


def build_issues_jql(
    project: str,
    *,
    assignee_id: str | None,
    all_users: bool,
    statuses: list[str],
    closed_statuses: list[str],
) -> str:
    """Build the JQL behind `get issues`.

    An explicit `statuses` filter replaces the default "hide what is closed" rule, so
    asking for a closed status actually returns something.
    """
    conditions = [f"project = {quote(project)}"]

    if assignee_id:
        conditions.append(f"assignee = {quote(assignee_id)}")
    elif not all_users:
        conditions.append("assignee = currentUser()")

    if statuses:
        conditions.append(f"status in ({', '.join(quote(status) for status in statuses)})")
    elif closed_statuses:
        conditions.append(f"status not in ({', '.join(quote(status) for status in closed_statuses)})")

    return f"{' AND '.join(conditions)} {ORDERING}"
