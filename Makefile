.PHONY: help install dev build test deploy clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make build      - Build all services"
	@echo "  make test       - Run all tests"
	@echo "  make deploy     - Deploy to Kubernetes"
	@echo "  make clean      - Clean build artifacts"

install:
	npm install
	cd backend && go mod download

dev:
	docker-compose up -d
	npm run dev

build:
	npm run build
	docker build -t claims-askes/api-gateway ./backend/api-gateway

test:
	npm run test
	cd backend && go test ./...

deploy:
	kubectl apply -k infrastructure/kubernetes/overlays/production

clean:
	rm -rf node_modules
	rm -rf dist
	rm -rf build
	docker-compose down -v
