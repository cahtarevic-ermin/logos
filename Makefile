.PHONY: all up down build logs migrate clean

# Start all services
all: up

# Build and start all services
up:
	docker compose up -d --build

# Stop all services
down:
	docker compose down

# Build images
build:
	docker compose build

# View logs
logs:
	docker compose logs -f

# View specific service logs
logs-api:
	docker compose logs -f api

logs-celery:
	docker compose logs -f celery

# Run migrations
migrate:
	docker compose exec api alembic upgrade head

# Clean everything (including volumes)
clean:
	docker compose down -v
	rm -rf uploads/*

# Restart services
restart:
	docker compose restart

# Shell into API container
shell:
	docker compose exec api /bin/bash

# Check status
status:
	docker compose ps

dev-rebuild:
	docker compose build --no-cache
	docker compose down
	docker compose up -d