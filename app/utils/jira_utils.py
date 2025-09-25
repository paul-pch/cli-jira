import typer
from jira import Issue


def get_transitions_from_issue(ctx: typer.Context, issue: Issue) -> list[str]:
    jira = ctx.obj.jira_client
    transitions = jira.transitions(issue)
    return (s["name"] for s in transitions)
