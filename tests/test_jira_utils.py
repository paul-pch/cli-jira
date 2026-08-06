from unittest.mock import MagicMock

import pytest
from jira import JIRA

from app.utils.exceptions import AmbiguousUserError, UserNotFoundError
from app.utils.jira import resolve_assignee


@pytest.fixture
def client() -> MagicMock:
    return MagicMock(spec=JIRA)


class TestResolveAssignee:
    @staticmethod
    def test_owned_uses_the_token_account(client: MagicMock) -> None:
        client.myself.return_value = {"accountId": "acc-me"}

        assert resolve_assignee(client, owned=True, owner=None) == {"id": "acc-me"}

    @staticmethod
    def test_owner_takes_precedence_over_owned(client: MagicMock) -> None:
        client.search_users.return_value = [MagicMock(accountId="acc-owner")]

        assert resolve_assignee(client, owned=True, owner="michel") == {"id": "acc-owner"}
        client.myself.assert_not_called()

    @staticmethod
    def test_no_assignee_requested(client: MagicMock) -> None:
        assert resolve_assignee(client, owned=False, owner=None) is None
        client.myself.assert_not_called()
        client.search_users.assert_not_called()

    @staticmethod
    def test_unknown_owner(client: MagicMock) -> None:
        client.search_users.return_value = []

        with pytest.raises(UserNotFoundError):
            resolve_assignee(client, owned=False, owner="personne")

    @staticmethod
    def test_ambiguous_owner(client: MagicMock) -> None:
        client.search_users.return_value = [MagicMock(), MagicMock()]

        with pytest.raises(AmbiguousUserError) as exc_info:
            resolve_assignee(client, owned=False, owner="michel")

        assert "jira get users --query michel" in str(exc_info.value)
