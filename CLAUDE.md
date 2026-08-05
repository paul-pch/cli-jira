# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cli-jira** is a Typer-based CLI for Jira operations, built for ops teams. It provides commands to create, get, and edit Jira issues. Built with Python 3.10+, packaged as a standalone binary via PyInstaller, and managed with `uv`.

## Architecture

```
main.py                  # Entry point — Typer app, callback injects AppState (config + JIRA client) into ctx.obj
app/
  get.py                 # `jira get` — subcommands: issue, issues, project, status, users
  create.py              # `jira create` — subcommand: issue
  edit.py                # `jira edit` — subcommand: issue
app/utils/
  jira.py                # JIRA client factory + helpers (transitions, statuses)
  display.py             # Rich rendering (tables, panels, markdown)
  utils.py               # Env var checks, config file discovery, Jira-to-MD formatting
  errors.py              # @handle_jira_errors decorator — catches JIRAError/ConnectionError etc.
  exceptions.py          # Custom exceptions (MissingEnvVarError, InvalidJiraStatusError)
  config_types.py        # TypedDicts: AppConfig, DefaultConfig
  app_state.py           # AppState dataclass — injected into Typer ctx.obj
config.toml              # Local config: default project, issue type, closed statuses, labels
tests/                   # pytest — fully mocked, no real Jira needed
```

Key patterns:
- Every command is decorated with `@handle_jira_errors` for uniform error handling.
- Commands access the JIRA client via `ctx.obj.jira_client` and config via `ctx.obj.config`.
- The `get.status` command branches: no argument → shows available statuses for default issue type; with an issue key → shows available transitions for that issue.

## Development Commands

All commands use `uv run` inside the managed venv.

```bash
make install              # Sync dependencies (uv sync --locked)
make test                 # Run tests with coverage (pytest --cov)
make lint                 # ruff check + ruff format (dry-run)
make format               # ruff format + ruff check --fix
make build                # PyInstaller standalone binary (dist/jira)
make all                  # install + test + build + integrate
make clean                # Remove venv, build artifacts, coverage
```

To run a single test:
```bash
uv run pytest tests/test_get.py -v
uv run pytest tests/test_get.py::test_issue -v
```

## Configuration

- **Env vars**: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN` (required)
- **Config file**: searched in order — `./config.toml`, `~/.config/jira/config.toml`, `/etc/jira/config.toml`
- The `config.toml` `[default]` section defines: project key, default issue type, max results, closed statuses, and default labels.

## CI

GitHub Actions runs `lint` (ruff check + format --check) and `test` (pytest) on every push/PR. No secrets needed.