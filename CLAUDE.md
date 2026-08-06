# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cli-jira** is a Typer-based CLI for Jira operations, built for ops teams. It provides commands to create, get, and edit Jira issues. Built with Python 3.10+, packaged as a standalone binary via PyInstaller, and managed with `uv`.

## Architecture

```
main.py                  # Entry point — Typer app, callback injects AppState (config + JIRA client) into ctx.obj
app/
  get.py                 # `jira get` — subcommands: issue, issues, projects, status, users
  create.py              # `jira create` — subcommand: issue
  edit.py                # `jira edit` — subcommand: issue
app/utils/
  jira.py                # JIRA client factory + helpers (transitions, statuses, assignee) — take the client, never ctx
  issue_fields.py        # ISSUE_FIELDS (fields fetched for display) + IssueFields builder (fields written)
  display.py             # Rich rendering (tables, panels, markdown)
  utils.py               # Env var checks, config file discovery, Markdown <-> Jira wiki conversion
  errors.py              # @handle_jira_errors decorator — catches CliJiraError/JIRAError/ConnectionError etc.
  exceptions.py          # CliJiraError base + one subclass per expected error
  config_types.py        # Frozen dataclasses: AppConfig (+ .resolve), DefaultConfig (+ .from_toml)
  app_state.py           # AppState dataclass — injected into Typer ctx.obj
config.toml              # Local config: default project, issue type, closed statuses, labels
tests/                   # pytest — fully mocked, no real Jira needed
```

Key patterns:

- **Everything flows through `ctx.obj`.** The `main.py` callback runs before every subcommand: it validates env vars, loads the TOML config, builds the JIRA client, and stores an `AppState` in `ctx.obj`. Commands never build a client themselves — they read `ctx.obj.jira_client` and `ctx.obj.config.default.<key>`.
- **Every command — and the `main.py` callback — is decorated with `@handle_jira_errors`**, which converts expected and Jira/network exceptions into a one-line CLI error and `exit 1`. Order matters: `@app.command()` first, then `@handle_jira_errors`.
- **Expected errors are raised, never printed.** Any error a command can foresee gets a `CliJiraError` subclass in `exceptions.py`, carrying its own French message; the decorator is the single place that renders it. Commands must not `console.print(...)` + `typer.Exit(1)` — add a subclass instead.
- **Config values are defaults, not constants.** Options like `--project`, `--issuetype`, `--labels` fall back to `config.toml` when omitted. Use `ctx.obj.config.resolve(<cli_option>, "<config_key>")` for that fallback — only `None` falls back, so an explicit `0`/`""` from the CLI is honoured. `labels` is additive: CLI labels are appended to the configured ones.
- **Descriptions cross a format boundary.** Input goes through `utils.description_to_jira()` (Markdown → Jira wiki markup) on write; output goes through `utils.format_description()` (Jira wiki → Markdown) before Rich renders it. Any new description-carrying command must do the same.
- **Write payloads go through `IssueFields`, read payloads through `ISSUE_FIELDS`.** `create` and `edit` never hand-build a `fields` dict: they fill an `IssueFields` and call `.to_jira()`, which omits every attribute left at `None`. A single `issue.update(fields=...)` per command — don't add a second round-trip for a new option. Fetch-for-display always asks for `ISSUE_FIELDS`.
- **Helpers in `utils/jira.py` take the client explicitly**, not `ctx`. Commands read `ctx.obj` and pass what's needed.
- `get.status` branches: no argument → available statuses for the default issue type (via the undocumented `project/{key}/statuses` endpoint, reached with `jira._get_json`); with an issue key → available transitions for that issue.
- Status edits are name-based: `edit.issue --status` matches the transition name case-insensitively and raises `InvalidJiraStatusError` if no transition matches.

### Language convention

Code, docstrings, and comments are in **English**; user-facing console output is in **French**. Keep new messages consistent with that split.

## Development Commands

All commands use `uv run` inside the managed venv.

```bash
make install              # Sync dependencies (uv sync --locked)
make test                 # Run tests with coverage (pytest --cov, HTML report in coverage-report/)
make lint                 # ruff check + ruff format (NOTE: rewrites files; CI uses --check)
make lint-check           # ruff check + ruff format --check (read-only, CI parity)
make format               # ruff format + ruff check --fix
make validate             # lint-check + test — run this before pushing
make build                # PyInstaller standalone binary (dist/jira)
make integrate            # Copy config.toml to ~/.config/jira/ and add dist/ to PATH via ~/.zshrc
make all                  # install + test + build + integrate
make clean                # Remove venv, build artifacts, coverage
```

To run a single test:

```bash
uv run pytest tests/test_get.py -v
uv run pytest tests/test_get.py::test_issue -v
```

To run the CLI without building the binary:

```bash
uv run python -m main get issues
```

### Linting

Ruff runs with `select = ["ALL"]` and `line-length = 130` (see `pyproject.toml` for the ignore list). New code must be clean under that ruleset — expect to need explicit type annotations, docstrings on public functions with a summary line, and `raise ... from e` on re-raises. Prefer fixing over adding `noqa`.

A pre-commit config is present (`ruff --fix` plus the full pytest suite on every commit); run `uv run pre-commit install` to enable it.

## Testing

Tests are fully mocked — no Jira server, no network, no secrets.

- `tests/conftest.py::mock_jira_client` is the fixture to request in nearly every test: it sets fake `JIRA_*` env vars and monkeypatches `app.utils.jira.get_jira_client` so the callback injects a `MagicMock(spec=JIRA)`. Assert against that mock's calls.
- `tests/conftest.py::make_issue` builds a `SimpleNamespace` shaped exactly as `display.py` expects. If you add a field to a display function, extend `make_issue` rather than hand-rolling fakes.
- Commands are invoked end-to-end through Typer's `CliRunner` (`runner.invoke(app, ["get", "issues"])`), so tests cover argument parsing and the `ctx.obj` wiring too.

## Configuration

- **Env vars** (all required, checked in the callback): `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`. The token is an Atlassian **API token**, not a password.
- **Config file**: searched in order — `./config.toml`, `~/.config/jira/config.toml`, `/etc/jira/config.toml`. The cwd copy wins, which matters when running from the repo root vs. anywhere else.
- The `[default]` section defines: project key, default issue type, max results, closed statuses (used to filter `get issues`), and default labels. Keep `DefaultConfig` in `config_types.py` in sync when adding keys — `DefaultConfig.from_toml` validates that every field is present and raises `InvalidConfigError` (rendered by the callback) otherwise.

## CI

GitHub Actions runs `lint` (`ruff check` + `ruff format --check`) and `test` (`pytest` with coverage) on every push to `main` and every PR. No secrets needed.
