from jira import JIRA, Issue

from app.utils.exceptions import InvalidRemoteLinkError

_SCHEMES = ("http://", "https://")


def parse_remote_link(raw: str) -> dict[str, str]:
    """Parse a `--link` value into the payload Jira expects.

    Accepts a bare URL, or `Titre=https://...` to give the link a label. The title
    defaults to the URL itself. An `=` inside the URL is not mistaken for a separator.
    """
    title, separator, url = raw.partition("=")

    if not separator or not url.startswith(_SCHEMES):
        title, url = raw, raw

    if not url.startswith(_SCHEMES):
        raise InvalidRemoteLinkError(raw)

    return {"url": url, "title": title}


def add_remote_links(jira: JIRA, issue: Issue, links: list[dict[str, str]]) -> None:
    """Attach already-parsed remote links to an issue."""
    for link in links:
        jira.add_simple_link(issue, object=link)
