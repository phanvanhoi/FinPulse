.PHONY: help dev up down build migrate test lint prod-up prod-down prod-build prod-logs prod-migrate prod-restart

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Development ---

dev: ## Start all services in development mode
	docker compose up --build

up: ## Start all services in background (dev)
	docker compose up -d --build

down: ## Stop all services (dev)
	docker compose down

build: ## Build all Docker images (dev)
	docker compose build

migrate: ## Run database migrations (dev)
	docker compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

test: ## Run backend tests
	docker compose exec backend pytest -v

lint: ## Run linting
	docker compose exec backend ruff check app/
	docker compose exec backend ruff format --check app/

format: ## Format code
	docker compose exec backend ruff format app/

logs: ## View service logs (dev)
	docker compose logs -f

logs-backend: ## View backend logs (dev)
	docker compose logs -f backend

logs-celery: ## View celery logs (dev)
	docker compose logs -f celery-worker

# --- Production (VPS) ---

prod-up: ## Start production stack on VPS
	docker compose -f docker-compose.prod.yml --env-file .env up -d --build

prod-down: ## Stop production stack
	docker compose -f docker-compose.prod.yml --env-file .env down

prod-build: ## Build production images
	docker compose -f docker-compose.prod.yml --env-file .env build

prod-logs: ## Tail production logs
	docker compose -f docker-compose.prod.yml --env-file .env logs -f

prod-migrate: ## Run migrations in production
	docker compose -f docker-compose.prod.yml --env-file .env exec backend alembic upgrade head

prod-restart: ## Restart production stack
	docker compose -f docker-compose.prod.yml --env-file .env restart

prod-ps: ## Show production container status
	docker compose -f docker-compose.prod.yml --env-file .env ps

prod-deploy: ## Full VPS deploy (build + start)
	bash scripts/deploy-vps.sh
