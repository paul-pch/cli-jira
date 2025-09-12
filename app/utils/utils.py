import os

import typer
from jira import JIRA, JIRAError

from app.utils.exceptions import MissingEnvVarError


def check_required_env_vars() -> dict[str, str]:
    env_vars = {
        "JIRA_URL": os.environ.get("JIRA_URL"),
        "JIRA_EMAIL": os.environ.get("JIRA_EMAIL"),
        "JIRA_TOKEN": os.environ.get("JIRA_TOKEN"),
    }

    if missing := [k for k, v in env_vars.items() if v is None]:
        raise MissingEnvVarError(missing)
    return env_vars


def get_jira_client(required_envs: dict[str, str]) -> JIRA:
    try:
        return JIRA(
            basic_auth=(required_envs["JIRA_EMAIL"], required_envs["JIRA_TOKEN"]), server=required_envs["JIRA_URL"], timeout=1
        )

    except JIRAError as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e

def get_external_config()-> dict[str, str]:
        
