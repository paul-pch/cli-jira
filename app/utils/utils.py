import os
from pathlib import Path

import typer
from jira import JIRA, Issue, JIRAError
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
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


def display_issue(issue: Issue) -> None:
    fields = issue.fields

    meta = Table(box=box.SIMPLE, show_header=False, padding=(0, 0))
    meta.add_column(style="bold cyan")
    meta.add_column()

    assignee = fields.assignee.displayName if fields.assignee else "Unassigned"
    labels = ", ".join(f'"{label}"' for label in fields.labels)

    meta.add_row("Key", issue.key)
    meta.add_row("Status", fields.status.name)
    meta.add_row("Assignee", assignee)
    meta.add_row("Labels", labels)
    meta.add_row("Created", fields.created[:10])

    content = Markdown(format_description(fields.description)) if fields.description else "[italic]No description[/italic]"

    layout = Table(box=None, padding=0, expand=True)
    layout.add_column(width=40)
    layout.add_column(ratio=1)
    layout.add_row(
        Panel(meta, title="Details"),
        Panel(content, title="Description"),
    )

    console.print(layout)


def display_issues(issues: list[Issue]) -> None:
    table = Table(
        box=box.ROUNDED,
        border_style="white",
        header_style="bold white",
        show_lines=False,
        expand=True,
    )
    table.add_column("Key", style="bold", width=12)
    table.add_column("Summary", ratio=3)
    table.add_column("Status", ratio=1, justify="center")
    table.add_column("Assignee", ratio=1)

    for issue in issues:
        table.add_row(
            issue.key,
            issue.fields.summary,
            issue.fields.status.name,
            getattr(issue.fields.assignee, "displayName", "—"),
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


def format_description(description: str) -> str:
    replacements = {
        "h1. ": "# ",
        "h2. ": "## ",
        "h3. ": "### ",
        "h4. ": "#### ",
        "??": "> ",
        "----": "---",
        "{code}": "```",
        "{quote}": "> ",
    }
    for jira, md in replacements.items():
        description = description.replace(jira, md)
    return description
