from pathlib import Path
from typing import Any

import tomllib
import typer

from app import create, delete, edit, get
from app.utils import jira, utils
from app.utils.app_state import AppState
from app.utils.config_types import AppConfig, DefaultConfig
from app.utils.errors import handle_jira_errors

app = typer.Typer(help="CLI jira for ops")


@app.callback()
@handle_jira_errors
def main(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    """Inject the JIRA client into the context."""
    env_vars = utils.check_required_env_vars()

    with Path(utils.find_config()).open("rb") as f:
        local_config: dict[str, Any] = tomllib.load(f)

    default = DefaultConfig.from_toml(local_config.get("default", {}))

    config = AppConfig(
        server=env_vars["server"],
        user=env_vars["user"],
        token=env_vars["token"],
        default=default,
    )

    ctx.obj = AppState(
        config=config,
        jira_client=jira.get_jira_client(env_vars),
        verbose=verbose,
    )


app.add_typer(create.app, name="create")
app.add_typer(get.app, name="get")
app.add_typer(edit.app, name="edit")
app.add_typer(delete.app, name="delete")


if __name__ == "__main__":
    app()
