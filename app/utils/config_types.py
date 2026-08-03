from typing import TypedDict


class DefaultConfig(TypedDict):
    project: str
    issue_type: str
    max_result: int
    user: str
    definition_closed: list[str]
    labels: list[str]


class AppConfig(TypedDict):
    server: str
    user: str
    token: str
    default: DefaultConfig
