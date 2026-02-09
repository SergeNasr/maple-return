# Run ruff linter
lint:
	uv run ruff check .

# Run ruff linter with auto-fix
lint-fix:
	uv run ruff check --fix .

# Run pytest tests
test:
	uv run pytest

# Run FastAPI dev server
run:
	uv run uvicorn maple_return.main:app --reload --host 127.0.0.1 --port 8000

# Install/sync dependencies
install:
	uv sync
