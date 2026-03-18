import os
from pathlib import Path

from app.utils.exceptions import MissingEnvVarError


def check_required_env_vars() -> dict[str, str]:
    env_vars = {
        "server": os.environ.get("JIRA_URL", ""),
        "user": os.environ.get("JIRA_EMAIL", ""),
        "token": os.environ.get("JIRA_TOKEN", ""),
    }

    if missing := [k for k, v in env_vars.items() if not v]:
        raise MissingEnvVarError(missing)

    return env_vars


def find_config() -> str:
    candidates = [
        f"{Path.cwd()}/config.toml",
        Path("~/.config/jira/config.toml").expanduser(),
        "/etc/jira/config.toml",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    error_msg = "config.toml introuvable"
    raise FileNotFoundError(error_msg)


def format_description(description: str) -> str:
    replacements = {
        "h1. ": "# ",
        "h2. ": "## ",
        "h3. ": "### ",
        "h4. ": "#### ",
        "??": "> ",
        "----": "---",
        "{code}": "```",
        "{quote}": "> ",
    }
    for jira, md in replacements.items():
        description = description.replace(jira, md)
    return description
