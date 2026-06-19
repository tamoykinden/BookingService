.PHONY: dev worker test lint

VENV := .venv
BIN := $(VENV)/bin

dev:
	$(BIN)/uvicorn app.main:app --reload --port 8001

worker:
	$(BIN)/celery -A app.celery_app worker --loglevel=info

test:
	$(BIN)/pytest -v

lint:
	$(BIN)/flake8 app/