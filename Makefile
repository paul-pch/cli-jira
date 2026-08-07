# Python CLI Project Makefile — driven by uv (https://docs.astral.sh/uv/)

.PHONY: all default install build integrate completion test lint lint-check format validate upgrade clean

default: install build integrate

all: install test build integrate

install:
	uv sync --locked
	@echo "Dependencies installed"

# shellingham loads its platform backend with importlib, which PyInstaller cannot see:
# without --collect-submodules, --install-completion fails to detect the shell.
build:
	uv run pyinstaller --onefile --name=jira --collect-submodules shellingham main.py
	@echo "Application built"

integrate:
	mkdir -p ~/.config/jira/
	cp -n config.toml ~/.config/jira/config.toml
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
	@echo "Application integrated into PATH"
	@echo "-> Please reload your terminal"

# Completion detects the shell by walking up the process tree, so the recipe must not
# run under make's /bin/sh. The trailing `:` keeps $SHELL from exec'ing the binary in
# place, which would leave /bin/sh as the visible parent.
completion: build
	@"$$SHELL" -c "$(CURDIR)/dist/jira --install-completion; :"
	@echo "-> Please reload your terminal"

test:
	uv run pytest tests --cov=app --cov-report=term --cov-report=html:coverage-report

lint:
	uv run ruff check .
	uv run ruff format .

# Read-only linting, exactly as CI runs it (no file is rewritten)
lint-check:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

# Full gate before pushing: same checks as the CI workflow
validate: lint-check test
	@echo "Validation passed"

upgrade:
	uv lock --upgrade
	uv sync
	@echo "Dependencies upgraded"

clean:
	rm -rf dist build *.egg-info coverage-report .coverage .pytest_cache .ruff_cache **/__pycache__ jira.spec
	rm -rf .venv
	@echo "Build artifacts removed"
