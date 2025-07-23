# cli-jira

A template for creating Python CLI applications with a modern development workflow, specifically for Jira interactions.

## Features

- Python CLI application using [Typer](https://typer.tiangolo.com/)
- Virtual environment management with Makefile
- Testing with pytest and coverage
- Executable building with PyInstaller
- Project metadata in pyproject.toml
- Automated development workflow with Makefile targets

## Installation

To install **cli-python-starter**, clone the repository and install the dependencies:

```bash
cd cli-jira
make install
```

## Usage

After installation, you can run the application:

```bash
jira --help
jira hello --name "Your Name"
```

## Development

The project includes a Makefile with the following targets:

- `make install`: Create virtual environment and install dependencies
- `make test`: Run tests with coverage
- `make build`: Create standalone executable
- `make integrate`: Add executable to PATH by modifying ~/.zshrc and reloading the shell configuration
- `make all`: Run install, test, and build targets

## Project Structure

```
cli-jira/
├── app/
│   └── main.py
├── tests/
│   └── test_main.py
├── venv/
├── dist/
├── build/
├── pyproject.toml
├── requirements.txt
└── Makefile
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
