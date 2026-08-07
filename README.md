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

Deux clés facultatives concernent les sprints :

```toml
[default]
board = "ST Scrum"                # utile seulement si plusieurs tableaux scrum couvrent le projet
sprint_field = "customfield_10020" # évite la découverte automatique du champ sprint
```

`board` sert à résoudre les sprints ; sans elle, le tableau est déduit du projet.
`sprint_field` est l'id du champ personnalisé portant le sprint : il diffère d'une instance
Jira à l'autre, donc la CLI le découvre via un appel à `fields()`. Le renseigner supprime
cet appel. Si la découverte échoue, le sprint n'est simplement pas affiché — seul
`jira edit issue --no-sprint`, qui doit écrire dans ce champ, s'arrête avec une erreur.

### Sprints

À la création, un ticket part **dans le sprint actif** par défaut :

```bash
jira create issue "Titre"                        # sprint actif
jira create issue "Titre" --sprint 'Sprint 42'   # sprint nommé, ou son id
jira create issue "Titre" --no-sprint            # backlog
jira edit issue ST-1060 --sprint current         # déplacer un ticket existant
jira edit issue ST-1060 --no-sprint              # renvoyer au backlog
jira get sprints                                 # sprints ouverts du tableau, avec leur id
jira get sprints --state closed                  # sprints clos
jira get issues --sprint current                 # filtrer les tickets sur un sprint
```

`--sprint` accepte un nom (insensible à la casse), un id numérique, ou `current` pour le
sprint actif. Seuls les sprints ouverts (`active`, `future`) sont résolus par leur nom :
Jira refuse d'ajouter un ticket à un sprint clos. Pour filtrer sur un sprint clos, passez
son id, que `jira get sprints --state closed` affiche.

Le sprint courant d'un ticket apparaît dans `jira get issue`.

Sans sprint actif ni tableau scrum, la création n'échoue pas : le ticket reste dans le
backlog avec un avertissement. Un `--sprint` explicite introuvable, lui, arrête la commande
avant toute écriture.

## Usage

After installation, you can run the application:

```bash
jira get projects
# or, without building the binary:
uv run python -m main get projects
```

### Complétion shell

La CLI fournit sa propre complétion (zsh, bash, fish, PowerShell) :

```bash
make completion
# équivalent à :
jira --install-completion
```

La commande écrit le script de complétion et l'appelle depuis le fichier de
configuration du shell courant ; rechargez le terminal ensuite. `jira --show-completion`
affiche le script sans rien modifier, si vous préférez l'installer vous-même.

La complétion ne lit ni `config.toml` ni les variables d'environnement Jira : elle
fonctionne même sans jeton configuré, et n'ouvre aucune connexion.

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
- `make completion`: Install shell completion for the current shell
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
