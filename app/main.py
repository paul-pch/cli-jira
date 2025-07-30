import typer
from jira import JIRA
from rich import print as rprint

app = typer.Typer()


@app.command()
def get_jira_projects(
    token: str = typer.Option(..., envvar="JIRA_TOKEN", help="Jira API token for authentication"),
    server: str = typer.Option(..., envvar="JIRA_URL", help="Jira server URL (e.g., https://your-domain.atlassian.net)"),
    user: str = typer.Option(..., envvar="JIRA_EMAIL", help="Jira user's email for authentication"),
) -> None:
    """Fetch and display Jira projects using provided token and server URL.

    The email, token and server can be provided as command-line options or
    set as environment variables JIRA_EMAIL, JIRA_TOKEN and JIRA_SERVER.
    """
    try:
        # Create JIRA client with token authentication

        # Authentication
        jira = JIRA(basic_auth=(user, token), server=server)
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


if __name__ == "__main__":
    app()
