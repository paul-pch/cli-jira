import os

import typer
from jira import JIRA, Issue, JIRAError
from rich.console import Console
from rich.table import Table

from app.utils.exceptions import MissingEnvVarError

console = Console()


def check_required_env_vars() -> dict[str, str]:
    env_vars = {
        "server": os.environ.get("JIRA_URL", ""),
        "user": os.environ.get("JIRA_EMAIL", ""),
        "token": os.environ.get("JIRA_TOKEN", ""),
    }

    if missing := [k for k, v in env_vars.items() if not v]:
        raise MissingEnvVarError(missing)

    return env_vars


def get_jira_client(required_envs: dict[str, str]) -> JIRA:
    try:
        return JIRA(basic_auth=(required_envs["user"], required_envs["token"]), server=required_envs["server"], timeout=1)

    except JIRAError as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


def display_issues(issues: list[Issue]) -> None:
    table = Table("Code", "Nom", "Statut", "Responsable")
    for issue in issues:
        table.add_row(
            issue.key,
            issue.fields.summary,
            issue.fields.status.name,
            getattr(issue.fields.assignee, "displayName", "None"),
        )
    console.print(table)
