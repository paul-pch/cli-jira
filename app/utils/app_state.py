from dataclasses import dataclass


@dataclass
class AppState:
    jira_client: object
    verbose: bool = False
    config: dict = None
