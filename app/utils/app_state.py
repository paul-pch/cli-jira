from dataclasses import dataclass


@dataclass
class AppState:
    config: dict[str, str]
    jira_client: object
    verbose: bool = False
