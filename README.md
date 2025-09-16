# cli-jira

## Installation

To install **cli-jira**, clone the repository and install the dependencies:

```bash
# Creates venv, install dependencies, build binary, add it to path
make
```

## Usage

After installation, you can run the application:

```bash
python -m main get projects
```

## Todo

* [ ] GET - Afficher la description dans un ticket
* [ ] CREATE - Ajouter le currentUser en assignee
* [ ] GET - Ajouter une option --all pour avoir tous les tickets et pas que ceux du currentuser


## Development

The project includes a Makefile with the following targets:

- `make install`: Create virtual environment and install dependencies
- `make test`: Run tests with coverage
- `make build`: Create standalone executable
- `make integrate`: Add executable to PATH by modifying ~/.zshrc and reloading the shell configuration
- `make all`: Run install, test, and build targets



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
