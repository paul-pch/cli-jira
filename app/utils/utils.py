import os
from pathlib import Path

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


def display_transitions(transitions: list[str], issue_type: str) -> None:
    table = Table(issue_type)
    for transition in transitions:
        table.add_row(
            transition,
        )
    console.print(table)


def find_config() -> str:
    candidates = [
        f"{Path.cwd()}/config.toml",
        Path("~/.config/jira/config.toml").expanduser(),
        "/etc/jira/config.toml",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    error_msg = "config.toml introuvable"
    raise FileNotFoundError(error_msg)
