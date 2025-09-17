class MissingEnvVarError(Exception):
    """Exception personnalisée pour les variables d'environnement manquantes."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Variables manquantes : {', '.join(missing)}")


class InvalidJiraStatusError(Exception):
    """Exception personnalisée pour les status des tickets jira."""

    def __init__(self, status: str) -> None:
        self.status = status
        super().__init__(f"Statut invalide : {status}")
