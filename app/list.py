import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Manage projects")
console = Console()


@app.command()
def project(ctx: typer.Context) -> None:
    try:
        jira = ctx.obj
        projects = jira.projects()
        table = Table("Code", "Nom")
        for project in projects:
            table.add_row(project.key, project.name)

        console.print(table)

    except (ConnectionError, TimeoutError, PermissionError) as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
