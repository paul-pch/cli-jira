import logging
from logging import getLogger

import typer
from jira import JIRA

logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
        logger.info("Available Jira Projects:")
        logger.info("-" * 30)
        for project in projects:
            logger.info("• %s: %s", project.key, project.name)

    except Exception:
        logger.exception("Error connecting to Jira")
        return


if __name__ == "__main__":
    app()
