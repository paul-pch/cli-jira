import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import typer
from jira import JIRAError

from app.utils.exceptions import CliJiraError

P = ParamSpec("P")
R = TypeVar("R")


def handle_jira_errors(func: Callable[P, R]) -> Callable[P, R]:
    """Catch expected CLI errors and Jira/network errors, and turn them into a French CLI error."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except (CliJiraError, JIRAError, ConnectionError, TimeoutError, PermissionError) as e:
            typer.echo(f"Erreur : {e}", err=True)
            raise typer.Exit(code=1) from e

    return wrapper
