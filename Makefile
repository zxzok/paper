POETRY?=poetry
NPM?=npm

setup:
	$(POETRY) install
	cd frontend && $(NPM) install

fmt:
	$(POETRY) run black backend tests/backend
	$(POETRY) run ruff format backend tests/backend

lint:
	$(POETRY) run ruff check backend tests/backend
	cd frontend && $(NPM) run lint

backend-test:
	$(POETRY) run pytest tests/backend

frontend-test:
	cd frontend && $(NPM) run test -- --reporter=list

test: backend-test frontend-test

build:
	docker compose build

dev:
	$(POETRY) run uvicorn backend.app.main:app --reload

compose-up:
	docker compose up --build

compose-down:
	docker compose down
