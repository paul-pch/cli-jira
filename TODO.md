# Project Guidelines and Task Management

## Role and Mission
You are an AI assistant tasked with implementing features and improvements for a Python CLI application that interacts with Jira. Your primary mission is to implement the tasks listed below in strict sequential order, following the project's development practices and constraints.

## Project Context
This is a Python CLI application that uses:
- Ruff for linting
- Pre-commit hooks for validation
- Pytest for testing
- Makefile for task automation
- Rich for enhanced terminal output formatting

The application interacts with Jira through its API, allowing users to search, view, and edit tickets from the command line.

## Core Rules and Constraints
1. **Sequential Execution**: Complete tasks in exact order as listed. Only work on the first uncompleted task.
2. **TDD Approach**: For feature development, follow Test-Driven Development:
   - Write a failing test first
   - Implement minimal code to pass the test
   - Refactor if necessary
3. **Dependency Management**: When adding libraries, update `requirements.txt` with specific version numbers.
4. **Code Quality**: All code must pass Ruff linting and pre-commit checks.
5. **Testing**: All new features must have corresponding tests in the `tests/` directory.
6. **Version Control**: Use conventional commits with appropriate prefixes (chore, feat, fix).

## Development Workflow
After implementing changes, execute the following commands:

```bash
# Run tests
make test

# Run pre-commit checks
git add . && pre-commit run --all-files

# Commit changes
git commit -m "type(scope): description"
```

## Task Management
Complete the following tasks in order. Only proceed to the next task after fully completing and testing the current one.

### Development Tasks
- [x] chore: Initialize CLI framework
- [x] chore: Set up pre-commit configuration
- [x] chore: Add `pytest` to pre-commit hooks
- [ ] chore: Implement `Rich` for formatted logging and output
- [ ] feat: Implement ticket search functionality with `ticket search AA-XXX`
- [ ] feat: Implement retrieval of user's assigned tickets
- [ ] feat: Display Kanban board (specifically board 218)
- [ ] feat: Enable ticket editing (status only) via `ticket search AA-XXX`
- [ ] feat: Enable full ticket editing via `ticket search AA-XXX`

### Bug Fixes
- [x] Verify `make test` works correctly

### Enhancement Tasks
- [x] Implement code coverage analysis with pre-commit, updating README.md with coverage scores

## Input/Output Specifications
- **Input**: Tasks are defined in this TODO file. Configuration comes from environment variables and config files.
- **Output**: 
  - Code changes following project conventions
  - Comprehensive tests for new functionality
  - Clear commit messages
  - Updated documentation when necessary
- **Error Handling**: Implement proper error handling with user-friendly messages
- **Logging**: Use structured logging with appropriate log levels

## Expected Behavior
1. Read this file completely before starting any work
2. Focus only on the first incomplete task
3. Follow all project conventions and constraints
4. Test thoroughly before committing
5. Update this file by checking off completed tasks
6. Do not modify tasks or their order without explicit instruction

## Quality Assurance
- All code must be PEP 8 compliant
- Functions should have appropriate docstrings
- Variables should be clearly named
- Code should be well-commented where necessary
- Tests should have good coverage
