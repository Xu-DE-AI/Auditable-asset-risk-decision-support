install:
	python -m pip install -e ".[dev]"
test:
	pytest
lint:
	ruff check src tests
demo:
	python -m reliability.cli demo --output artifacts
api:
	uvicorn reliability.api:app --host 0.0.0.0 --port 8000
mcp:
	reliability-mcp
