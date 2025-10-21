# Makefile for Schedule DND project
# Author: DmitrTRC
# Description: Common development tasks automation

.PHONY: help install dev-install clean test lint format type-check security all-checks run build docs

# Variables
PYTHON := poetry run python
PYTEST := poetry run pytest
BLACK := poetry run black
ISORT := poetry run isort
MYPY := poetry run mypy
PYLINT := poetry run pylint
BANDIT := poetry run bandit

# Directories
SRC_DIR := src/schedule_dnd
TEST_DIR := tests
DOCS_DIR := docs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Schedule DND - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	poetry install --no-dev
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

dev-install: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	poetry install
	poetry run pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

clean: ## Clean up cache and temporary files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf dist/ build/ htmlcov/ .coverage coverage.xml
	@echo "$(GREEN)✓ Cleaned up$(NC)"

##@ Code Quality

format: ## Format code with Black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(BLACK) $(SRC_DIR) $(TEST_DIR)
	$(ISORT) $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run linting checks
	@echo "$(BLUE)Running linting...$(NC)"
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR)
	$(ISORT) --check-only $(SRC_DIR) $(TEST_DIR)
	$(PYLINT) $(SRC_DIR)
	@echo "$(GREEN)✓ Linting passed$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Type checking...$(NC)"
	$(MYPY) $(SRC_DIR)
	@echo "$(GREEN)✓ Type checking passed$(NC)"

security: ## Run security checks with Bandit
	@echo "$(BLUE)Running security scan...$(NC)"
	$(BANDIT) -r $(SRC_DIR) -f screen
	@echo "$(GREEN)✓ Security check passed$(NC)"

all-checks: format lint type-check security ## Run all code quality checks
	@echo "$(GREEN)✓ All checks passed!$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTEST) -v
	@echo "$(GREEN)✓ Tests passed$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) tests/unit/ -v
	@echo "$(GREEN)✓ Unit tests passed$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) tests/integration/ -v
	@echo "$(GREEN)✓ Integration tests passed$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) --cov --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(PYTEST) -f

##@ Application

run: ## Run the application
	@echo "$(BLUE)Starting Schedule DND...$(NC)"
	poetry run schedule-dnd

run-dev: ## Run the application in development mode
	@echo "$(BLUE)Starting Schedule DND (development mode)...$(NC)"
	SCHEDULE_DND_ENV=development poetry run schedule-dnd

build: ## Build distribution package
	@echo "$(BLUE)Building package...$(NC)"
	poetry build
	@echo "$(GREEN)✓ Package built in dist/$(NC)"

##@ Documentation

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation server not yet implemented$(NC)"

##@ Git

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	poetry run pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

##@ CI/CD

ci: all-checks test ## Run full CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline completed successfully!$(NC)"

##@ Utilities

info: ## Display project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "$(GREEN)Name:$(NC)         schedule-dnd"
	@echo "$(GREEN)Version:$(NC)      2.0.0"
	@echo "$(GREEN)Author:$(NC)       DmitrTRC"
	@echo "$(GREEN)Python:$(NC)       $(shell poetry run python --version)"
	@echo "$(GREEN)Poetry:$(NC)       $(shell poetry --version)"
	@echo ""
	@echo "$(BLUE)Project Structure:$(NC)"
	@tree -L 2 -I '__pycache__|*.pyc|.pytest_cache|.mypy_cache|htmlcov' src/ 2>/dev/null || echo "  (install 'tree' for better output)"

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	poetry update
	poetry run pre-commit autoupdate
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

env-info: ## Show virtual environment information
	@echo "$(BLUE)Virtual Environment Information:$(NC)"
	@poetry env info
	@echo ""
	@echo "$(GREEN)To activate the environment:$(NC)"
	@echo "  Linux/macOS: source $(poetry env info --path)/bin/activate"
	@echo "  Windows:     $(poetry env info --path)\\Scripts\\activate"

.DEFAULT_GOAL := help
