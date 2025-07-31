import os

import typer
from jira import JIRA
from jira.exceptions import JIRAError


class JiraConfigError(Exception):

    """Raised when the required JIRA environment variables are missing."""


def get_jira_client() -> JIRA:
    server = os.getenv("JIRA_URL")
    user = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_TOKEN")

    missing = [var for var, val in {"JIRA_URL": server, "JIRA_EMAIL": user, "JIRA_TOKEN": token}.items() if not val]

    if missing:
        raise JiraConfigError(f"Missing required environment variables: {', '.join(missing)}")

    try:
        return JIRA(basic_auth=(user, token), server=server)
    except JIRAError as e:
        raise typer.Exit(code=1, message=f"Failed to connect to JIRA: {e}")
