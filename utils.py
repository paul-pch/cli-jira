import os
from types import SimpleNamespace

import typer
from jira import JIRA, JIRAError


class MissingEnvVarError(Exception):
    """Exception personnalisée pour les variables d'environnement manquantes."""


def check_required_env_vars() -> SimpleNamespace:
    env_vars = {
        "server": os.environ.get("JIRA_URL"),
        "user": os.environ.get("JIRA_EMAIL"),
        "token": os.environ.get("JIRA_TOKEN"),
    }

    if missing := [k for k, v in env_vars.items() if not v]:
        msg = f"Variables manquantes : {', '.join(missing)}"
        raise MissingEnvVarError(msg)
    return SimpleNamespace(**env_vars)


def get_jira_client() -> JIRA:
    try:
        required = check_required_env_vars()
        return JIRA(basic_auth=(required.user, required.token), server=required.server, timeout=1)

    except JIRAError as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e

    except MissingEnvVarError as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e
