import os
import re
from pathlib import Path

from app.utils.exceptions import MissingEnvVarError

_heading_re = re.compile(r"^(#{1,6})\s+(.+)$")
_bullet_re = re.compile(r"^(\s*[-*])+\s+(.+)$")
_ordered_re = re.compile(r"^(\s*-)*\s*\d+\.\s+(.+)$")
_hr_re = re.compile(r"^(\s*[-*_]{3,}\s*)+$")
_blockquote_re = re.compile(r"^>\s?(.*)$")
_inline_code_re = re.compile(r"`([^`]+)`")
_strikethrough_re = re.compile(r"~~(.+?)~~")
_bold_re = re.compile(r"\*\*(.+?)\*\*")
_italic_re = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


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


def description_to_jira(description: str) -> str:
    """Convert Markdown to Jira wiki markup so the description renders correctly in Jira."""
    lines = description.splitlines()
    result: list[str] = []

    for line in lines:
        # Headings: # → h1., ## → h2., etc.
        heading_match = _heading_re.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            level = min(level, 6)
            result.append(f"h{level}. {heading_match.group(2)}")
            continue

        # Unordered list: * or -
        bullet_match = _bullet_re.match(line)
        if bullet_match:
            indent = "  " * (bullet_match.group(1).count("-") - 1) if bullet_match.group(1) else ""
            result.append(f"{indent}* {bullet_match.group(2)}")
            continue

        # Ordered list: 1.
        ordered_match = _ordered_re.match(line)
        if ordered_match:
            indent = "  " * (ordered_match.group(1).count("-") - 1) if ordered_match.group(1) else ""
            result.append(f"{indent}# {ordered_match.group(2)}")
            continue

        # Horizontal rule
        if _hr_re.match(line):
            result.append("----")
            continue

        # Blockquote
        if _blockquote_re.match(line):
            result.append(f"?? {line.lstrip('> ')}")
            continue

        # Inline code: backticks are left as-is (Jira wiki markup has no reliable inline code syntax)
        # No conversion needed — backticks will render as plain text in Jira

        # Strikethrough
        transformed = _strikethrough_re.sub(r"- \1 -", line)

        # Bold
        transformed = _bold_re.sub(r"*\1*", transformed)

        # Italic
        transformed = _italic_re.sub(r"_\1_", transformed)

        result.append(transformed)

    return "\n".join(result)
