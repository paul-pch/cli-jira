class MissingEnvVarError(Exception):
    """Raised when a required environment variable is missing."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Variables manquantes : {', '.join(missing)}")


class InvalidJiraStatusError(Exception):
    """Raised when a Jira issue status is invalid."""

    def __init__(self, status: str) -> None:
        self.status = status
        super().__init__(f"Statut invalide : {status}")
