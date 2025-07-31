# Makefile for the-fetus project

.PHONY: help install format lint type-check test clean dev-setup

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies only
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

dev-setup:  ## Set up development environment
	python setup_dev.py

format:  ## Format code with Black and isort
	black .
	isort .

lint:  ## Run flake8 linter
	flake8 .

type-check:  ## Run mypy type checker
	mypy .

pre-commit-all:  ## Run all pre-commit hooks on all files
	pre-commit run --all-files

clean:  ## Remove Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

run:  ## Run the Flask application
	python app.py

test:  ## Run tests (add your test command here)
	echo "No tests configured yet"

check:  ## Run all checks (format, lint, type-check)
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
