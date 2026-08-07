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


class InvalidIssueLinkTypeError(CliJiraError):
    """Raised when no Jira link type matches the requested relation."""

    def __init__(self, link_type: str, available: list[str]) -> None:
        self.link_type = link_type
        self.available = available
        super().__init__(f"type de lien invalide : {link_type}. Types disponibles : {', '.join(available)}")


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


class ConflictingJqlOptionsError(CliJiraError):
    """Raised when a raw JQL query is combined with the filter options it would override."""

    def __init__(self) -> None:
        super().__init__("--jql remplace toute la requête : il ne peut pas être combiné aux options de filtre")


class ConflictingParentOptionsError(CliJiraError):
    """Raised when attaching and detaching a parent are asked for at once."""

    def __init__(self) -> None:
        super().__init__("--parent et --no-parent sont contradictoires")


class DeletionCancelledError(CliJiraError):
    """Raised when the user declines the deletion prompt."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"suppression de {key} annulée")


class NothingToUpdateError(CliJiraError):
    """Raised when an edit command is called without any field to change."""

    def __init__(self) -> None:
        super().__init__("aucune modification demandée")


class SprintNotFoundError(CliJiraError):
    """Raised when no open sprint matches the requested name."""

    def __init__(self, sprint: str, available: list[str]) -> None:
        self.sprint = sprint
        self.available = available
        message = f"sprint introuvable : {sprint}"
        if available:
            message += f". Sprints ouverts : {', '.join(available)}"
        super().__init__(message)


class AmbiguousSprintError(CliJiraError):
    """Raised when several open sprints match the requested one."""

    def __init__(self, sprint: str, available: list[str]) -> None:
        self.sprint = sprint
        self.available = available
        super().__init__(f"plusieurs sprints correspondent à {sprint} : {', '.join(available)}. Précisez-le par son id")


class NoActiveSprintError(CliJiraError):
    """Raised when the active sprint is asked for and none is running."""

    def __init__(self, project: str) -> None:
        self.project = project
        super().__init__(f"aucun sprint actif sur le projet {project}")


class SprintFieldNotFoundError(CliJiraError):
    """Raised when the sprint custom field can't be located on this Jira instance."""

    def __init__(self) -> None:
        super().__init__(
            "champ sprint introuvable sur cette instance Jira. Renseignez `sprint_field` dans config.toml "
            "(son id, de la forme customfield_10020)"
        )


class ConflictingSprintOptionsError(CliJiraError):
    """Raised when joining and leaving a sprint are asked for at once."""

    def __init__(self) -> None:
        super().__init__("--sprint et --no-sprint sont contradictoires")


class BoardNotFoundError(CliJiraError):
    """Raised when no scrum board serves the project."""

    def __init__(self, project: str, board: str | None) -> None:
        self.project = project
        self.board = board
        wanted = f' "{board}"' if board else ""
        super().__init__(f"tableau scrum{wanted} introuvable pour le projet {project}")


class AmbiguousBoardError(CliJiraError):
    """Raised when several scrum boards serve the project."""

    def __init__(self, project: str, available: list[str]) -> None:
        self.project = project
        self.available = available
        super().__init__(f"plusieurs tableaux scrum pour {project} : {', '.join(available)}. Renseignez `board` dans config.toml")


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
