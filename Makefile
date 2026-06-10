.PHONY: install lint build run compose-up compose-down logs test-local test-compose clean check help

# Install Node dependencies for Newman/Spectral/Prism
install:
	npm install

# Lint OpenAPI contracts with Spectral
lint:
	npx spectral lint contracts/*.yaml

# Build Docker image
build:
	docker build -t ai-vision-a4:v1.0.0 .

# Run API container standalone
run:
	docker run --rm --name ai-vision-a4 -p 8000:8000 --env-file .env ai-vision-a4:v1.0.0

# Run service locally without Docker
run-local:
	uvicorn ai_vision.main:app --app-dir src --host 0.0.0.0 --port 8000

# Compose commands
compose-up:
	docker compose up -d --build

compose-down:
	docker compose down

compose-down-v:
	docker compose down -v

logs:
	docker compose logs -f

# Run Newman tests locally
test-local:
	mkdir -p reports && npm run test:local

# Run Newman tests on compose stack
test-compose:
	mkdir -p reports && npm run test:compose

# Run all tests (local server must be running)
test-all: test-local

# Check Docker Compose syntax
check:
	docker compose config --quiet

# Show container status
status:
	docker compose ps

# Clean up
clean:
	docker compose down -v
	docker image prune -f

# Help
help:
	@echo "AI Vision Service (A4) - Makefile Commands"
	@echo ""
	@echo "  install       - Install Node dependencies"
	@echo "  lint          - Lint OpenAPI contracts"
	@echo "  build         - Build Docker image"
	@echo "  run           - Run Docker container standalone"
	@echo "  run-local     - Run service locally (Python/uvicorn)"
	@echo "  compose-up    - Build and start Compose stack"
	@echo "  compose-down  - Stop and remove Compose stack"
	@echo "  logs          - Follow all logs"
	@echo "  test-local    - Run Newman tests locally"
	@echo "  test-compose  - Run Newman tests on compose stack"
	@echo "  check         - Validate docker-compose.yml"
	@echo "  status        - Show container status"
	@echo "  clean         - Clean up containers and images"
	@echo "  help          - Show this help message"
