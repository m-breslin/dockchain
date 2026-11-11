
# ---------------------------------------------------------
# Dockchain Makefile
# ---------------------------------------------------------
# Provides easy, descriptive commands to install, run,
# test, lint, build, and maintain Dockchain using uv.
# ---------------------------------------------------------

UV := uv
DOCKER := docker
RUNTIME_IMAGE := dockchain-runtime:local

# -------------------------
# Install all development dependencies and pre-commit hooks
# -------------------------
.PHONY: install-deps
install-deps:
	@echo "📦 Installing Dockchain dependencies..."
	$(UV) sync --group dev --all-extras
	@echo "🔧 Installing pre-commit hooks..."
	$(UV) run pre-commit install
	@echo "✅ Dockchain development environment ready!"


# -------------------------
# Synchronize dependencies with uv.lock
# -------------------------
.PHONY: sync-deps
sync-deps:
	@echo "🔄 Synchronizing Dockchain dependencies..."
	$(UV) sync --group dev --all-extras
	@echo "✅ Dependencies synchronized!"


# -------------------------
# Upgrade dependencies and update uv.lock
# -------------------------
.PHONY: update-deps
update-deps:
	@echo "⬆️ Updating Dockchain dependencies..."
	$(UV) lock --upgrade
	$(UV) sync --group dev --all-extras
	@echo "✅ Dependencies updated!"


# -------------------------
# Run the Dockchain CLI
# -------------------------
.PHONY: dockchain-help
dockchain-help:
	@echo "🚀 Displaying Dockchain CLI commands..."
	$(UV) run dockchain --help


# -------------------------
# Run unit and integration tests
# -------------------------
.PHONY: test
test:
	@echo "🧪 Running Dockchain tests..."
	$(UV) run pytest
	@echo "✅ Tests completed!"


# -------------------------
# Run Ruff linting
# -------------------------
.PHONY: lint
lint:
	@echo "🔍 Checking Dockchain code..."
	$(UV) run ruff check .
	@echo "✅ Linting completed!"


# -------------------------
# Format Dockchain code
# -------------------------
.PHONY: format
format:
	@echo "✨ Formatting Dockchain code..."
	$(UV) run ruff check --fix .
	$(UV) run ruff format .
	@echo "✅ Formatting completed!"


# -------------------------
# Check formatting without modifying files
# -------------------------
.PHONY: format-check
format-check:
	@echo "🔍 Checking code formatting..."
	$(UV) run ruff format --check .
	@echo "✅ Formatting check passed!"


# -------------------------
# Run static type checking
# -------------------------
.PHONY: type-check
type-check:
	@echo "🔍 Running MyPy..."
	$(UV) run mypy src/
	@echo "✅ Type checking completed!"


# -------------------------
# Run all quality checks
# -------------------------
.PHONY: check
check: lint format-check type-check test
	@echo "✅ All Dockchain checks passed!"


# -------------------------
# Build the Python package
# -------------------------
.PHONY: build
build:
	@echo "📦 Building Dockchain distribution..."
	$(UV) build
	@echo "✅ Package build completed!"


# -------------------------
# Build the Dockchain runtime Docker image
# -------------------------
.PHONY: docker-build
docker-build:
	@echo "🐳 Building Dockchain runtime image..."
	$(DOCKER) build -f runtime/Dockerfile -t $(RUNTIME_IMAGE) .
	@echo "✅ Runtime image built!"


# -------------------------
# Remove generated development artifacts
# -------------------------
.PHONY: clean
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
	@echo "✅ Cleanup completed!"
