# Development Setup Guide

This guide will help you set up the development environment with pre-commit hooks and code formatting tools.

## Quick Setup

Run the setup script to install all development tools:

```bash
python setup_dev.py
```

## Manual Setup

If you prefer to set up manually:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

3. **Run pre-commit on all files (to see current state):**
   ```bash
   pre-commit run --all-files
   ```

## Available Tools

### Code Formatting
- **Black**: Automatic code formatting
  ```bash
  black .                    # Format all files
  black fetusapp/           # Format specific directory
  ```

- **isort**: Import statement sorting
  ```bash
  isort .                   # Sort imports in all files
  ```

### Code Quality
- **flake8**: Linting and style checking
  ```bash
  flake8 .                  # Check all files
  flake8 fetusapp/          # Check specific directory
  ```

- **mypy**: Type checking (optional)
  ```bash
  mypy .                    # Type check all files
  ```

### Pre-commit Hooks
Pre-commit hooks will automatically run on every commit and check:
- Code formatting (Black)
- Import sorting (isort)
- Linting (flake8)
- Trailing whitespace
- End of file fixing
- YAML syntax
- Large file detection
- Merge conflict detection
- Debug statement detection

## Make Commands

If you have `make` installed, you can use these convenient commands:

```bash
make help          # Show all available commands
make dev-setup     # Set up development environment
make format        # Format code with Black and isort
make lint          # Run flake8 linter
make type-check    # Run mypy type checker
make check         # Run all checks (format, lint, type-check)
make clean         # Remove Python cache files
make run           # Run the Flask application
```

## Configuration Files

- `.pre-commit-config.yaml`: Pre-commit hook configuration
- `pyproject.toml`: Black, isort, and mypy configuration
- `Makefile`: Convenient development commands

## Skipping Pre-commit Hooks

If you need to commit without running pre-commit hooks (not recommended):

```bash
git commit --no-verify -m "Your commit message"
```

## Updating Pre-commit Hooks

To update all pre-commit hooks to their latest versions:

```bash
pre-commit autoupdate
```
