# cli-jira

[![CI](https://github.com/paul-pch/cli-jira/actions/workflows/ci.yml/badge.svg)](https://github.com/paul-pch/cli-jira/actions/workflows/ci.yml)

## Installation

To install **cli-jira**, clone the repository. Dependencies are managed with
[uv](https://docs.astral.sh/uv/):

```bash
# Installs dependencies (via uv), builds the binary, adds it to PATH
make
```

## Configuration

**cli-jira** s'authentifie avec un **jeton d'API Jira** (et non votre mot de passe).
Créez-en un depuis [Atlassian account settings → Security → API tokens](https://id.atlassian.com/manage-profile/security/api-tokens),
puis exportez les trois variables d'environnement requises :

```bash
export JIRA_URL="https://votre-domaine.atlassian.net"
export JIRA_EMAIL="votre.email@example.com"
export JIRA_TOKEN="votre-jeton-d-api"
```

Si l'une d'elles est manquante, la CLI s'arrête avec un message indiquant laquelle.

Le reste de la configuration (projet par défaut, type de ticket, statuts considérés
comme fermés, labels par défaut) se trouve dans un `config.toml`, cherché dans cet ordre :

1. `./config.toml`
2. `~/.config/jira/config.toml`
3. `/etc/jira/config.toml`

## Usage

After installation, you can run the application:

```bash
jira get projects
# or, without building the binary:
uv run python -m main get projects
```

## Todo

Fonctionnalités en attente d'implémentation :

### `edit`


### `get`

* [ ] GET - Lister les statuts d'un type de ticket autre que celui par défaut

### Divers

* [ ] DELETE - Supprimer un ticket
* [ ] CLI - Complétion shell (zsh / bash)


## Development

The project includes a Makefile, driven by `uv`, with the following targets:

- `make install`: Sync the uv-managed virtual environment with `uv.lock`
- `make test`: Run tests with coverage
- `make lint`: Check linting and formatting with ruff (rewrites files)
- `make lint-check`: Read-only lint, exactly as CI runs it
- `make format`: Auto-fix linting and formatting with ruff
- `make validate`: Full gate before pushing — `lint-check` + `test`, same checks as CI
- `make build`: Create standalone executable
- `make integrate`: Add executable to PATH by modifying ~/.zshrc and reloading the shell configuration
- `make upgrade`: Upgrade dependencies and refresh `uv.lock`
- `make all`: Run install, test, build, and integrate targets
- `make clean`: Remove the virtual environment and build artifacts

Requires [uv](https://docs.astral.sh/uv/) to be installed.

### CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main` and on every pull request:

- `lint`: `ruff check` and `ruff format --check`
- `test`: `pytest` with coverage

Tests are fully mocked (no real Jira server needed), so CI requires no secrets.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
