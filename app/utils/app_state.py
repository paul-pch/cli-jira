from dataclasses import dataclass

from jira import JIRA

from app.utils.config_types import AppConfig


@dataclass(frozen=True, slots=True)
class AppState:
    config: AppConfig
    jira_client: JIRA
    verbose: bool = False
