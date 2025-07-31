import typer

from app import project

app = typer.Typer(help="CLI jira for ops")

app.add_typer(project.app, name="project")


if __name__ == "__main__":
    app()
