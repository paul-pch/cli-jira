import os
from pathlib import Path

from app.utils.exceptions import MissingEnvVarError


def check_required_env_vars() -> dict[str, str]:
    required = {
        "server": "JIRA_URL",
        "user": "JIRA_EMAIL",
        "token": "JIRA_TOKEN",
    }
    env_vars = {key: os.environ.get(name, "") for key, name in required.items()}

    if missing := [required[k] for k, v in env_vars.items() if not v]:
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
