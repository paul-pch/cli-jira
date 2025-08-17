# cli-jira

## Installation

To install **cli-python-starter**, clone the repository and install the dependencies:

```bash
# Creates venv, install dependencies, build binary, add it to path
make
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
