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
  jira.py                # JIRA client factory + helpers (transitions, statuses)
  display.py             # Rich rendering (tables, panels, markdown)
  utils.py               # Env var checks, config file discovery, Markdown <-> Jira wiki conversion
  errors.py              # @handle_jira_errors decorator — catches JIRAError/ConnectionError etc.
  exceptions.py          # Custom exceptions (MissingEnvVarError, InvalidJiraStatusError)
  config_types.py        # TypedDicts: AppConfig, DefaultConfig
  app_state.py           # AppState dataclass — injected into Typer ctx.obj
config.toml              # Local config: default project, issue type, closed statuses, labels
tests/                   # pytest — fully mocked, no real Jira needed
```

Key patterns:

- **Everything flows through `ctx.obj`.** The `main.py` callback runs before every subcommand: it validates env vars, loads the TOML config, builds the JIRA client, and stores an `AppState` in `ctx.obj`. Commands never build a client themselves — they read `ctx.obj.jira_client` and `ctx.obj.config["default"][...]`.
- **Every command is decorated with `@handle_jira_errors`**, which converts Jira/network exceptions into a one-line CLI error and `exit 1`. Order matters: `@app.command()` first, then `@handle_jira_errors`.
- **Config values are defaults, not constants.** Options like `--project`, `--issuetype`, `--labels` fall back to `config.toml` when omitted (see `create.py`). `labels` is additive: CLI labels are appended to the configured ones.
- **Descriptions cross a format boundary.** Input goes through `utils.description_to_jira()` (Markdown → Jira wiki markup) on write; output goes through `utils.format_description()` (Jira wiki → Markdown) before Rich renders it. Any new description-carrying command must do the same.
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
make format               # ruff format + ruff check --fix
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
- The `[default]` section defines: project key, default issue type, max results, closed statuses (used to filter `get issues`), and default labels. Keep `DefaultConfig` in `config_types.py` in sync when adding keys.

## CI

GitHub Actions runs `lint` (`ruff check` + `ruff format --check`) and `test` (`pytest` with coverage) on every push to `main` and every PR. No secrets needed.
