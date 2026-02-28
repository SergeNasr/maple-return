# Project conventions

## Package manager
- Use **uv** as the package manager (not pip, poetry, etc.)
- Install dependencies: `just install` (runs `uv sync`)

## Task runner
- Use the **justfile** for common commands. Prefer `just <command>` over running tools directly.
  - `just lint` — run ruff linter
  - `just lint-fix` — run ruff linter with auto-fix
  - `just test` — run pytest
  - `just run` — start FastAPI dev server (port 8001)
  - `just install` — install/sync dependencies
