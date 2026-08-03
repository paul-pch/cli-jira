from pathlib import Path
from typing import TYPE_CHECKING

import tomllib
import typer

from app import create, edit, get
from app.utils import jira, utils
from app.utils.app_state import AppState
from app.utils.config_types import AppConfig

if TYPE_CHECKING:
    from app.utils.config_types import DefaultConfig

app = typer.Typer(help="CLI jira for ops")


@app.callback()
def main(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    """Injecte le client JIRA dans le contexte."""
    env_vars = utils.check_required_env_vars()
    with Path(utils.find_config()).open("rb") as f:
        local_config: dict[str, DefaultConfig] = tomllib.load(f)

    config = AppConfig(
        server=env_vars["server"],
        user=env_vars["user"],
        token=env_vars["token"],
        default=local_config["default"],
    )

    ctx.obj = AppState(
        config=config,
        jira_client=jira.get_jira_client(env_vars),
        verbose=verbose,
    )


app.add_typer(create.app, name="create")
app.add_typer(get.app, name="get")
app.add_typer(edit.app, name="edit")


if __name__ == "__main__":
    app()
