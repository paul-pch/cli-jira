from jira import Issue
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from app.utils import utils

console = Console()

def default_table() -> Table:
    return Table(
        box=box.ROUNDED,
        border_style="white",
        header_style="bold white",
        show_lines=False,
        expand=True,
    )


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

    content = Markdown(utils.format_description(fields.description)) if fields.description else "[italic]No description[/italic]"

    layout = Table(box=None, padding=0, expand=True)
    layout.add_column(width=40)
    layout.add_column(ratio=1)
    layout.add_row(
        Panel(meta, title="Details"),
        Panel(content, title="Description"),
    )

    console.print(layout)


def display_issues(issues: list[Issue]) -> None:
    table = default_table()
    table.add_column("Key", style="bold", width=12)
    table.add_column("Summary", min_width=40)
    table.add_column("Status", min_width=15)
    table.add_column("Assignee", min_width=20)

    for issue in issues:
        table.add_row(
            issue.key,
            escape(issue.fields.summary),
            issue.fields.status.name,
            getattr(issue.fields.assignee, "displayName", "—"),
        )
    console.print(table)


def display_tuples(columns: list[str], rows: list[tuple[str, ...]] | list[str]) -> None:
    table = default_table()
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    console.print(table)

