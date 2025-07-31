import typer
from rich import print as rprint

from app import utils

app = typer.Typer(help="Manage projects")


@app.command()
def list() -> None:
    """Fetch and display Jira projects using provided token and server URL.

    The email, token and server can be provided as command-line options or
    set as environment variables JIRA_EMAIL, JIRA_TOKEN and JIRA_SERVER.
    """
    try:
        # Create JIRA client with token authentication

        # Authentication
        jira = utils.get_jira_client()
        # Fetch projects from Jira
        projects = jira.projects()

        # Display projects
        rprint("Available Jira Projects:")
        rprint("-" * 30)
        for project in projects:
            rprint(f"• {project.key}: {project.name}")

    except (ConnectionError, TimeoutError, PermissionError) as e:
        rprint(f"Error connecting to Jira: {e}")
        return
