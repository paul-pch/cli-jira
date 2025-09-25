# Python CLI Project Makefile Template

# Variables
PYTHON := python3
VENV_DIR := venv
VENV_BIN := $(VENV_DIR)/bin
PIP := $(VENV_BIN)/pip
PYTHON_CMD := $(VENV_BIN)/python
SOURCE_DIR := app

.PHONY: install build integrate clean upgrade

default: venv install build integrate

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

install: venv
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

build: install
# 	--exclude-module pkg_resources à retirer quand la lib sera mise à jour
	$(VENV_BIN)/pyinstaller --exclude-module pkg_resources --onefile --name=jira main.py
	@echo "Application built"

integrate:
	mkdir -p ~/.config/jira/
	cp -n config.toml ~/.config/jira/config.toml
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
	@echo "Application integrated into PATH"
	@echo "-> Please reload your terminal"

upgrade: venv
	@echo "Checking for outdated packages..."
	$(PIP) list --outdated
	@echo "Upgrading packages..."
	$(PIP) install --upgrade -r requirements.txt
	@echo "Verifying dependencies..."
	$(PIP) check
	@echo "Upgrading complete. All dependencies are verified."
clean:
	rm -rf dist build *.egg-info coverage-report .coverage .pytest_cache **/__pycache__ jira.spec
	rm -rf venv
	@echo "Build artifacts removed"
