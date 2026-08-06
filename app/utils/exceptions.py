class CliJiraError(Exception):
    """Base class for expected CLI errors.

    Anything deriving from it is caught by `@handle_jira_errors` and rendered as a
    one-line French message, so commands only ever have to `raise`.
    """


class MissingEnvVarError(CliJiraError):
    """Raised when a required environment variable is missing."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"variable(s) d'environnement manquante(s) : {', '.join(missing)}")


class InvalidConfigError(CliJiraError):
    """Raised when the config file is missing required keys."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"configuration invalide, clés manquantes dans la section [default] : {', '.join(missing)}")


class InvalidJiraStatusError(CliJiraError):
    """Raised when a Jira issue status is invalid."""

    def __init__(self, status: str, available: list[str] | None = None) -> None:
        self.status = status
        self.available = available or []
        message = f"statut invalide : {status}"
        if self.available:
            message += f". Statuts disponibles : {', '.join(self.available)}"
        super().__init__(message)


class IssueTypeNotFoundError(CliJiraError):
    """Raised when an issue type doesn't exist for the configured project."""

    def __init__(self, issue_type: str, project: str) -> None:
        self.issue_type = issue_type
        self.project = project
        super().__init__(f'type de ticket "{issue_type}" introuvable pour le projet {project}')


class InvalidRemoteLinkError(CliJiraError):
    """Raised when a --link value isn't a usable URL."""

    def __init__(self, raw: str) -> None:
        self.raw = raw
        super().__init__(f"lien invalide : {raw}. Attendu : une URL http(s), éventuellement préfixée par `Titre=`")


class NothingToUpdateError(CliJiraError):
    """Raised when an edit command is called without any field to change."""

    def __init__(self) -> None:
        super().__init__("aucune modification demandée")


class UserNotFoundError(CliJiraError):
    """Raised when no Jira user matches the requested owner."""

    def __init__(self, query: str) -> None:
        self.query = query
        super().__init__(f"aucun utilisateur ne correspond à {query}")


class AmbiguousUserError(CliJiraError):
    """Raised when several Jira users match the requested owner."""

    def __init__(self, query: str) -> None:
        self.query = query
        super().__init__(f"plusieurs utilisateurs correspondent à {query}. Précisez avec `jira get users --query {query}`")
