from pathlib import Path
from typing import Any

import tomllib
import typer
from rich.console import Console

from app import create, edit, get
from app.utils import jira, utils
from app.utils.app_state import AppState
from app.utils.config_types import AppConfig, DefaultConfig
from app.utils.exceptions import InvalidConfigError, MissingEnvVarError

app = typer.Typer(help="CLI jira for ops")
console = Console()


@app.callback()
def main(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    """Inject the JIRA client into the context."""
    try:
        env_vars = utils.check_required_env_vars()
    except MissingEnvVarError as e:
        console.print(f"[yellow]Variable(s) d'environnement manquante(s) : {', '.join(e.missing)}[/yellow]")
        raise typer.Exit(code=1) from e

    with Path(utils.find_config()).open("rb") as f:
        local_config: dict[str, Any] = tomllib.load(f)

    try:
        default = DefaultConfig.from_toml(local_config.get("default", {}))
    except InvalidConfigError as e:
        console.print(f"[yellow]Configuration invalide : {e}[/yellow]")
        raise typer.Exit(code=1) from e

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


if __name__ == "__main__":
    app()
