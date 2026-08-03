# cli-jira

## Installation

To install **cli-jira**, clone the repository. Dependencies are managed with
[uv](https://docs.astral.sh/uv/):

```bash
# Installs dependencies (via uv), builds the binary, adds it to PATH
make
```

## Usage

After installation, you can run the application:

```bash
jira get projects
# or, without building the binary:
uv run python -m main get projects
```

## Todo

* [ ] CHORE - S - Faire un avertissement de variables manquantes plus gentil
* [ ] GET - Ajouter une option --all pour avoir tous les tickets et pas que ceux du currentuser
* [ ] GET - Récupérer la liste des status disponibles pour un type de ticket
* [ ] CREATE - Passer le status du ticket directement à la création
* [ ] UPDATE - Editer la liste des labels partielle ou entière
* [ ] UPDATE - Pouvoir passer un ticket dans un status "terminé" ou équivalent facilement


## Development

The project includes a Makefile, driven by `uv`, with the following targets:

- `make install`: Sync the uv-managed virtual environment with `uv.lock`
- `make test`: Run tests with coverage
- `make lint`: Check linting and formatting with ruff
- `make format`: Auto-fix linting and formatting with ruff
- `make build`: Create standalone executable
- `make integrate`: Add executable to PATH by modifying ~/.zshrc and reloading the shell configuration
- `make upgrade`: Upgrade dependencies and refresh `uv.lock`
- `make all`: Run install, test, build, and integrate targets
- `make clean`: Remove the virtual environment and build artifacts

Requires [uv](https://docs.astral.sh/uv/) to be installed.



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
