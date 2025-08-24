# Luminous Nix Development Makefile
# Consciousness-first development workflows

.PHONY: help install dev test lint format clean build release

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Luminous Nix Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	poetry install

dev: ## Install all dependencies including dev tools
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	poetry install --with dev
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)Development environment ready!$(NC)"

test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	poetry run pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "$(GREEN)Running unit tests...$(NC)"
	poetry run pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "$(GREEN)Running integration tests...$(NC)"
	poetry run pytest tests/integration/ -v

test-consciousness: ## Test adaptive personas and learning
	@echo "$(GREEN)Testing consciousness systems...$(NC)"
	poetry run python test_adaptive_personas.py
	poetry run python test_consciousness.py || true

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	poetry run pytest tests/ \
		--cov=src/luminous_nix \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

lint: ## Run all linters
	@echo "$(GREEN)Running linters...$(NC)"
	poetry run ruff check src/ tests/
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/
	poetry run mypy src/ --ignore-missing-imports || true

format: ## Format code automatically
	@echo "$(GREEN)Formatting code...$(NC)"
	poetry run black src/ tests/
	poetry run isort src/ tests/
	poetry run ruff check --fix src/ tests/

security: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	poetry run bandit -r src/ -ll
	poetry run safety check || true
	poetry run pip-audit || true

clean: ## Clean build artifacts
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	@echo "$(GREEN)Building distribution packages...$(NC)"
	poetry build
	@echo "$(GREEN)Packages built in dist/$(NC)"

# Development workflows
start-api: ## Start the LLM API server
	@echo "$(GREEN)Starting LLM API server...$(NC)"
	poetry run python start_llm_api.py --port 8002

start-ollama: ## Start Ollama integration
	@echo "$(GREEN)Starting Ollama integration...$(NC)"
	./luminous-nix-launcher.sh start

test-ollama: ## Test Ollama integration
	@echo "$(GREEN)Testing Ollama flow...$(NC)"
	poetry run python test_ollama_flow.py

demo: ## Run interactive demo
	@echo "$(GREEN)Starting interactive demo...$(NC)"
	./luminous-nix-launcher.sh demo

# CI/CD simulation
ci-local: ## Run CI pipeline locally
	@echo "$(GREEN)Running CI pipeline locally...$(NC)"
	@make lint
	@make test-coverage
	@make security
	@make build
	@echo "$(GREEN)CI pipeline passed!$(NC)"

pre-commit: ## Run pre-commit hooks
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

# Documentation
docs: ## Build documentation
	@echo "$(GREEN)Building documentation...$(NC)"
	mkdocs build --clean --strict

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation at http://localhost:8000$(NC)"
	mkdocs serve

# Release management
version: ## Show current version
	@poetry version

bump-patch: ## Bump patch version (0.0.X)
	poetry version patch
	@echo "$(GREEN)Version bumped to $$(poetry version -s)$(NC)"

bump-minor: ## Bump minor version (0.X.0)
	poetry version minor
	@echo "$(GREEN)Version bumped to $$(poetry version -s)$(NC)"

bump-major: ## Bump major version (X.0.0)
	poetry version major
	@echo "$(GREEN)Version bumped to $$(poetry version -s)$(NC)"

release: build ## Create a release
	@echo "$(GREEN)Creating release...$(NC)"
	@echo "Current version: $$(poetry version -s)"
	@echo "Don't forget to:"
	@echo "  1. Commit version bump"
	@echo "  2. Create git tag: git tag v$$(poetry version -s)"
	@echo "  3. Push tag: git push origin v$$(poetry version -s)"
	@echo "  4. GitHub Actions will handle the rest!"

# Special consciousness-first commands
awaken: ## Start your development session mindfully
	@echo "$(GREEN)🧘 Setting sacred intention...$(NC)"
	@sleep 2
	@echo "$(GREEN)✨ Ready to manifest consciousness in code$(NC)"
	@make dev
	@echo ""
	@echo "$(YELLOW)Remember: Every function is a prayer, every test a meditation$(NC)"

flow: ## Enter flow state with all services
	@echo "$(GREEN)🌊 Entering flow state...$(NC)"
	@make clean
	@make dev
	@make start-api &
	@sleep 3
	@make test-consciousness
	@echo "$(GREEN)🌊 All systems flowing in harmony$(NC)"

# Database setup
setup-trinity: ## Install Data Trinity databases
	@echo "$(GREEN)Installing Data Trinity...$(NC)"
	poetry add duckdb chromadb kuzu
	@echo "$(GREEN)Data Trinity installed!$(NC)"

# Benchmarking
benchmark: ## Run performance benchmarks
	@echo "$(GREEN)Running benchmarks...$(NC)"
	poetry run pytest tests/benchmarks/ \
		--benchmark-only \
		--benchmark-json=benchmark.json
	@echo "$(GREEN)Benchmark results in benchmark.json$(NC)"

# Quick checks
check: ## Quick check before committing
	@echo "$(GREEN)Running quick checks...$(NC)"
	@make format
	@make lint
	@make test-unit
	@echo "$(GREEN)✅ Ready to commit!$(NC)"

.DEFAULT_GOAL := help