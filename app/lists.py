import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="List the ressources availables for the current user")
console = Console()


@app.command()
def project(ctx: typer.Context) -> None:
    """
    List available projects
    """
    try:
        jira = ctx.obj.jira_client
        projects = jira.projects()
        table = Table("Code", "Nom")
        for project in projects:
            table.add_row(project.key, project.name)

        console.print(table)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def issues(ctx: typer.Context) -> None:
    """
    List owned issues # TODO owed ou autre chose ?
    """
    try:
        jira = ctx.obj.jira_client

        jql = "assignee = currentUser() ORDER BY updated DESC"
        # issues = jira.search_issues(jql, maxResults=50)  # TODO Utiliser la version maxResults de config

        issues = jira.search_issues(jql, startAt=0, maxResults=50, fields="key,summary,assignee,status,created")
        console.print(issues)
        table = Table("Code", "Nom", "Statut", "Responsable")
        for issue in issues:
            table.add_row(
                issue.key,
                issue.fields.summary,
                issue.fields.status.name,
                getattr(issue.fields.assignee, "displayName", "None"),
            )

        console.print(table)
    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
