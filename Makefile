# Unit tests only
unit-test:
	uv run pytest -m "not integration"

# Integration tests only
int-test:
	uv run pytest -m "integration"

# All tests
test:
	uv run pytest

lint:
	uv run ruff

typecheck:
	uv run ty check 