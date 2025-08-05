import os
from types import SimpleNamespace

import pytest

import utils


class TestUtils:
    @staticmethod
    def test_check_required_env_vars_present() -> None:
        os.environ["JIRA_URL"] = "https://jira.example.com"
        os.environ["JIRA_EMAIL"] = "user@example.com"
        os.environ["JIRA_TOKEN"] = "secrettoken"  # noqa: S105

        result = utils.check_required_env_vars()
        assert isinstance(result, SimpleNamespace)
        assert result.server == "https://jira.example.com"
        assert result.user == "user@example.com"
        assert result.token

    @staticmethod
    def test_check_required_env_vars_missing() -> None:
        os.environ.pop("JIRA_URL", None)
        os.environ.pop("JIRA_TOKEN", None)
        os.environ["JIRA_EMAIL"] = "user@example.com"

        with pytest.raises(utils.MissingEnvVarError) as exc_info:
            utils.check_required_env_vars()

        assert "Variables manquantes" in str(exc_info.value)
        assert "server" in str(exc_info.value)
        assert "token" in str(exc_info.value)
