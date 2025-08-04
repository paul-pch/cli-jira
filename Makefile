# Python CLI Project Makefile Template

# Variables
PYTHON := python3
VENV_DIR := venv
VENV_BIN := $(VENV_DIR)/bin
PIP := $(VENV_BIN)/pip
PYTHON_CMD := $(VENV_BIN)/python
SOURCE_DIR := app
TEST_DIR := tests

# Virtual environment management
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV_DIR)

# Dependencies management
.PHONY: install
install: venv
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

.PHONY: update-deps
update-deps:
	$(PIP) install --upgrade -r requirements.txt
	@echo "Dependencies updated"

# Testing
.PHONY: test
test:
	$(PYTHON_CMD) -m pytest $(TEST_DIR) --cov=$(SOURCE_DIR) --cov-report=html:coverage-report
	@echo "Tests completed"

# Building
.PHONY: build
build:
	pyinstaller --onefile --name=jira $(SOURCE_DIR)/main.py
	@echo "Application built"

# Integration
.PHONY: integrate
integrate:
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
	@echo "Application integrated into shell"

# Clean
.PHONY: clean
clean:
	rm -rf dist build *.egg-info coverage-report .coverage .pytest_cache **/__pycache__
	@echo "Build artifacts removed"

# Default target
.PHONY: all
all: install test build
