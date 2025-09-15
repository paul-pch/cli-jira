from pathlib import Path

import tomllib
import typer

from app import get, lists
from app.utils import utils
from app.utils.app_state import AppState

app = typer.Typer(help="CLI jira for ops")


@app.callback()
def main(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    """Injecte le client JIRA dans le contexte."""
    env_vars = utils.check_required_env_vars()

    with Path("config.toml").open("rb") as f:
        local_config = tomllib.load(f)

    ctx.obj = AppState(
        config=env_vars.update(local_config),
        jira_client=utils.get_jira_client(env_vars),
        verbose=verbose,
    )


app.add_typer(lists.app, name="list")
app.add_typer(get.app, name="get")

if __name__ == "__main__":
    app()
