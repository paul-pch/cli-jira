from dataclasses import dataclass, fields
from typing import Any, TypeVar

from app.utils.exceptions import InvalidConfigError

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class DefaultConfig:
    project: str
    issue_type: str
    max_result: int
    user: str
    definition_closed: list[str]
    labels: list[str]

    @classmethod
    def from_toml(cls, section: dict[str, Any]) -> "DefaultConfig":
        """Build the [default] section, reporting missing keys instead of raising a raw KeyError."""
        expected = {f.name for f in fields(cls)}

        if missing := sorted(expected - section.keys()):
            raise InvalidConfigError(missing)

        return cls(**{name: section[name] for name in expected})


@dataclass(frozen=True, slots=True)
class AppConfig:
    server: str
    user: str
    token: str
    default: DefaultConfig

    def resolve(self, override: T | None, key: str) -> T:
        """Return the CLI override when one is given, else the configured default.

        Only `None` falls back, so an explicit `0` or `""` from the CLI is honoured.
        """
        return override if override is not None else getattr(self.default, key)
