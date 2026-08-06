import pytest

from app.utils.exceptions import InvalidRemoteLinkError
from app.utils.remote_links import parse_remote_link


class TestParseRemoteLink:
    @staticmethod
    def test_bare_url_is_its_own_title() -> None:
        assert parse_remote_link("https://example.com/x") == {
            "url": "https://example.com/x",
            "title": "https://example.com/x",
        }

    @staticmethod
    def test_titled_link() -> None:
        assert parse_remote_link("MR=https://gitlab.com/x/-/merge_requests/1") == {
            "url": "https://gitlab.com/x/-/merge_requests/1",
            "title": "MR",
        }

    @staticmethod
    def test_query_string_is_not_a_separator() -> None:
        """The first `=` belongs to the URL here, not to a title prefix."""
        assert parse_remote_link("https://example.com/?a=b") == {
            "url": "https://example.com/?a=b",
            "title": "https://example.com/?a=b",
        }

    @staticmethod
    def test_title_keeps_the_full_url_including_its_query_string() -> None:
        assert parse_remote_link("Doc=https://example.com/?a=b") == {
            "url": "https://example.com/?a=b",
            "title": "Doc",
        }

    @staticmethod
    @pytest.mark.parametrize("raw", ["example.com", "Titre=example.com", "ftp://example.com", ""])
    def test_rejects_anything_that_is_not_an_http_url(raw: str) -> None:
        with pytest.raises(InvalidRemoteLinkError):
            parse_remote_link(raw)
