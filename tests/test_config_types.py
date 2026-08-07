import pytest

from app.utils.config_types import AppConfig, DefaultConfig
from app.utils.exceptions import InvalidConfigError

VALID_SECTION = {
    "project": "ST",
    "issue_type": "Story Technique",
    "max_result": 50,
    "user": "admin",
    "definition_closed": ["Terminé"],
    "labels": ["OPS"],
}


class TestDefaultConfig:
    @staticmethod
    def test_from_toml_builds_the_section() -> None:
        default = DefaultConfig.from_toml(VALID_SECTION)

        assert default.project == "ST"
        assert default.max_result == VALID_SECTION["max_result"]
        assert default.labels == ["OPS"]

    @staticmethod
    def test_from_toml_ignores_unknown_keys() -> None:
        default = DefaultConfig.from_toml({**VALID_SECTION, "unknown": "value"})

        assert default.project == "ST"

    @staticmethod
    def test_board_is_optional() -> None:
        """Existing config.toml files predate the key, so its absence must not be an error."""
        assert DefaultConfig.from_toml(VALID_SECTION).board is None
        assert DefaultConfig.from_toml({**VALID_SECTION, "board": "ST Scrum"}).board == "ST Scrum"

    @staticmethod
    def test_from_toml_reports_every_missing_key() -> None:
        """A missing key used to surface as a raw KeyError in the middle of a command."""
        section = {k: v for k, v in VALID_SECTION.items() if k not in {"project", "labels"}}

        with pytest.raises(InvalidConfigError) as exc_info:
            DefaultConfig.from_toml(section)

        assert exc_info.value.missing == ["labels", "project"]
        assert "project" in str(exc_info.value)


class TestAppConfig:
    @staticmethod
    def _config() -> AppConfig:
        return AppConfig(
            server="https://jira.example.com",
            user="user@example.com",
            token="secrettoken",  # noqa: S106
            default=DefaultConfig.from_toml(VALID_SECTION),
        )

    def test_resolve_falls_back_on_the_config(self) -> None:
        assert self._config().resolve(None, "project") == "ST"

    def test_resolve_prefers_the_cli_override(self) -> None:
        assert self._config().resolve("OPS", "project") == "OPS"

    def test_resolve_honours_a_falsy_override(self) -> None:
        """Only None falls back, so an explicit 0 is not mistaken for "not provided"."""
        assert self._config().resolve(0, "max_result") == 0
