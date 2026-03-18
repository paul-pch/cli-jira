import typer
from jira import JIRA, Issue, JIRAError


def get_jira_client(required_envs: dict[str, str]) -> JIRA:
    try:
        return JIRA(basic_auth=(required_envs["user"], required_envs["token"]), server=required_envs["server"], timeout=5)

    except JIRAError as e:
        typer.echo(f"Erreur : {e}", err=True)
        raise typer.Exit(code=1) from e


def get_transitions_from_issue(ctx: typer.Context, issue: Issue) -> list[str]:
    jira = ctx.obj.jira_client
    return [status["name"] for status in jira.transitions(issue)]
