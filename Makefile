# STAX (Story & Test Automation eXtractor) - Docker Management

.PHONY: help build run dev prod stop clean logs shell test

# Default target
help:
	@echo "STAX (Story & Test Automation eXtractor) - Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  build      Build Docker image"
	@echo "  dev        Run development environment"
	@echo "  run        Run standalone container"
	@echo ""
	@echo "Production:"
	@echo "  prod       Run production environment"
	@echo "  prod-nginx Run production with nginx reverse proxy"
	@echo ""
	@echo "Management:"
	@echo "  stop       Stop all containers"
	@echo "  clean      Clean up containers and images"
	@echo "  logs       View container logs"
	@echo "  shell      Open shell in running container"
	@echo ""
	@echo "Utilities:"
	@echo "  test       Run tests in container"
	@echo "  backup     Backup application data"
	@echo "  restore    Restore application data"

# Build Docker image
build:
	@echo "Building Docker image..."
	docker build -t stax-app .

# Run development environment
dev: build
	@echo "Starting development environment..."
	docker-compose up --build

# Run development environment in background
dev-bg: build
	@echo "Starting development environment in background..."
	docker-compose up --build -d

# Run standalone container
run: build
	@echo "Running standalone container..."
	docker run -d \
		--name stax-app \
		-p 5001:5001 \
		--env-file .env \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/snapshots:/app/snapshots \
		ado-story-extractor

# Run production environment
prod: build
	@echo "Starting production environment..."
	docker-compose -f docker-compose.prod.yml up --build -d

# Run production with nginx
prod-nginx: build
	@echo "Starting production environment with nginx..."
	docker-compose -f docker-compose.prod.yml --profile production up --build -d

# Stop all containers
stop:
	@echo "Stopping containers..."
	docker-compose down
	docker-compose -f docker-compose.prod.yml down
	docker stop stax-app 2>/dev/null || true

# Clean up containers and images
clean: stop
	@echo "Cleaning up containers and images..."
	docker rm stax-app 2>/dev/null || true
	docker rmi stax-app 2>/dev/null || true
	docker system prune -f

# View container logs
logs:
	@echo "Viewing container logs..."
	docker-compose logs -f stax-app

# Open shell in running container
shell:
	@echo "Opening shell in container..."
	docker exec -it stax-app /bin/bash

# Run tests in container
test: build
	@echo "Running tests in container..."
	docker run --rm \
		--env-file .env.docker \
		-v $(PWD)/tests:/app/tests \
		ado-story-extractor \
		python -m pytest tests/ -v

# Backup application data
backup:
	@echo "Backing up application data..."
	@mkdir -p backups
	docker run --rm \
		-v ado-story-extractor_app_logs:/data/logs \
		-v ado-story-extractor_app_snapshots:/data/snapshots \
		-v ado-story-extractor_app_config:/data/config \
		-v $(PWD)/backups:/backup \
		alpine tar czf /backup/ado-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "Backup completed in backups/ directory"

# Restore application data (usage: make restore BACKUP=filename.tar.gz)
restore:
	@if [ -z "$(BACKUP)" ]; then echo "Usage: make restore BACKUP=filename.tar.gz"; exit 1; fi
	@echo "Restoring application data from $(BACKUP)..."
	docker run --rm \
		-v ado-story-extractor_app_logs:/data/logs \
		-v ado-story-extractor_app_snapshots:/data/snapshots \
		-v ado-story-extractor_app_config:/data/config \
		-v $(PWD)/backups:/backup \
		alpine tar xzf /backup/$(BACKUP) -C /data
	@echo "Restore completed"

# Check application health
health:
	@echo "Checking application health..."
	@curl -f http://localhost:5001/api/health && echo "✅ Application is healthy" || echo "❌ Application is unhealthy"

# Monitor resource usage
monitor:
	@echo "Monitoring resource usage..."
	docker stats ado-story-extractor

# Update application
update:
	@echo "Updating application..."
	git pull origin main
	docker-compose up --build -d

# Full deployment (for CI/CD)
deploy: clean build prod health
	@echo "✅ Deployment completed successfully"
