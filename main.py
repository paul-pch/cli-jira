import typer

from app import list
from utils import get_jira_client

app = typer.Typer(help="CLI jira for ops")


@app.callback()
def main(ctx: typer.Context) -> None:
    """Injecte le client JIRA dans le contexte."""
    ctx.obj = get_jira_client()


app.add_typer(list.app, name="list")

if __name__ == "__main__":
    app()
