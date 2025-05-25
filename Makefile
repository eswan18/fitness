# Unit tests only
test:
	uv run pytest -m "not integration"

# Integration tests only
int-test:
	uv run pytest -m "integration"

# All tests
all-test:
	uv run pytest

lint:
	uv run ruff check

format:
	uv run ruff format

typecheck:
	uv run ty check 
