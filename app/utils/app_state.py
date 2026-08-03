from dataclasses import dataclass

from app.utils.config_types import AppConfig


@dataclass
class AppState:
    config: AppConfig
    jira_client: object
    verbose: bool = False
