import typer

from app import lists
from app.utils.utils import get_jira_client

app = typer.Typer(help="CLI jira for ops")


@app.callback()
def main(ctx: typer.Context) -> None:
    """Injecte le client JIRA dans le contexte."""
    ctx.obj = get_jira_client()


app.add_typer(lists.app, name="list")

if __name__ == "__main__":
    app()
