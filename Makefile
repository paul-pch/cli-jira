# Python CLI Project Makefile Template

# Variables
PYTHON := python3
VENV_DIR := venv
VENV_BIN := $(VENV_DIR)/bin
PIP := $(VENV_BIN)/pip
PYTHON_CMD := $(VENV_BIN)/python
SOURCE_DIR := app

.PHONY: venv install build integrate clean

default: venv install build integrate

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

install: venv
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

build: install
	pyinstaller --onefile --name=jira main.py
	@echo "Application built"

integrate:
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
	@echo "Application integrated into PATH"
	@echo "-> Please reload your terminal"

clean:
	rm -rf dist build *.egg-info coverage-report .coverage .pytest_cache **/__pycache__ jira.spec
	rm -rf venv
	@echo "Build artifacts removed"
