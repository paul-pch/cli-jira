# Python CLI Project Makefile — driven by uv (https://docs.astral.sh/uv/)

.PHONY: all default install build integrate test lint format upgrade clean

default: install build integrate

all: install test build integrate

install:
	uv sync --locked
	@echo "Dependencies installed"

build:
	uv run pyinstaller --onefile --name=jira main.py
	@echo "Application built"

integrate:
	mkdir -p ~/.config/jira/
	cp -n config.toml ~/.config/jira/config.toml
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
	@echo "Application integrated into PATH"
	@echo "-> Please reload your terminal"

test:
	uv run pytest tests --cov=app --cov-report=term --cov-report=html:coverage-report

lint:
	uv run ruff check .
	uv run ruff format .

format:
	uv run ruff format .
	uv run ruff check --fix .

upgrade:
	uv lock --upgrade
	uv sync
	@echo "Dependencies upgraded"

clean:
	rm -rf dist build *.egg-info coverage-report .coverage .pytest_cache .ruff_cache **/__pycache__ jira.spec
	rm -rf .venv
	@echo "Build artifacts removed"
