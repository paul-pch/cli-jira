class MissingEnvVarError(Exception):
    """Exception personnalisée pour les variables d'environnement manquantes."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Variables manquantes : {', '.join(missing)}")
