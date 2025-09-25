from pathlib import Path

import tomllib
import typer

from app import create, edit, get
from app.utils import utils
from app.utils.app_state import AppState

app = typer.Typer(help="CLI jira for ops")


@app.callback()
def main(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    """Injecte le client JIRA dans le contexte."""
    env_vars = utils.check_required_env_vars()
    with Path(utils.find_config()).open("rb") as f:
        local_config = tomllib.load(f)

    ctx.obj = AppState(
        config={**env_vars, **local_config},
        jira_client=utils.get_jira_client(env_vars),
        verbose=verbose,
    )


app.add_typer(create.app, name="create")
app.add_typer(get.app, name="get")
app.add_typer(edit.app, name="edit")


if __name__ == "__main__":
    app()
