# Fluxora Infrastructure Makefile
# Provides convenience targets for common operations

.PHONY: help up down build ps logs shell lint validate clean test

COMPOSE_FILES := -f docker-compose.yml
COMPOSE_PROD  := -f docker-compose.yml -f docker-compose.prod.yml
COMPOSE_TEST  := -f docker-compose.test.yml
ENV_FILE      := --env-file .env

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker Compose ─────────────────────────────────────────────────────────────
up: ## Start all services (development)
	@test -f .env || (echo "Missing .env file. Copy .env.example → .env and fill values." && exit 1)
	docker compose $(COMPOSE_FILES) $(ENV_FILE) up -d

down: ## Stop all services
	docker compose $(COMPOSE_FILES) down

down-v: ## Stop all services and remove volumes (destructive!)
	docker compose $(COMPOSE_FILES) down -v

build: ## Build all Docker images
	docker compose $(COMPOSE_FILES) build --no-cache

build-backend: ## Build only the backend image
	docker compose $(COMPOSE_FILES) build --no-cache backend

build-frontend: ## Build only the frontend image
	docker compose $(COMPOSE_FILES) build --no-cache frontend

ps: ## Show running containers
	docker compose $(COMPOSE_FILES) ps

logs: ## Tail logs for all services
	docker compose $(COMPOSE_FILES) logs -f

logs-backend: ## Tail backend logs
	docker compose $(COMPOSE_FILES) logs -f backend

logs-db: ## Tail database logs
	docker compose $(COMPOSE_FILES) logs -f database

shell-backend: ## Open shell in backend container
	docker compose $(COMPOSE_FILES) exec backend sh

shell-db: ## Open MySQL shell in database container
	docker compose $(COMPOSE_FILES) exec database \
	  mysql -u$${MYSQL_USER:-appuser} -p$${MYSQL_PASSWORD:-dev-password} $${MYSQL_DATABASE:-fluxoradb}

restart: ## Restart all services
	docker compose $(COMPOSE_FILES) restart

restart-backend: ## Restart backend service
	docker compose $(COMPOSE_FILES) restart backend

# ── Testing ────────────────────────────────────────────────────────────────────
test: ## Run integration tests
	docker compose $(COMPOSE_TEST) up --abort-on-container-exit --exit-code-from backend-test
	docker compose $(COMPOSE_TEST) down -v

# ── Production ─────────────────────────────────────────────────────────────────
prod-up: ## Start production stack
	@test -f .env.prod || (echo "Missing .env.prod file." && exit 1)
	docker compose $(COMPOSE_PROD) --env-file .env.prod up -d

prod-down: ## Stop production stack
	docker compose $(COMPOSE_PROD) down

# ── Linting & Validation ───────────────────────────────────────────────────────
lint-yaml: ## Lint all YAML files
	yamllint -c .yamllint .

lint-tf: ## Lint Terraform files
	cd terraform && terraform fmt -check -recursive
	cd terraform && tflint --recursive

validate-tf: ## Validate Terraform configuration
	cd terraform && terraform init -backend=false && terraform validate

lint-k8s: ## Lint Kubernetes manifests with kubeval
	@which kubeval > /dev/null 2>&1 || (echo "Install kubeval: https://github.com/instrumenta/kubeval" && exit 1)
	find kubernetes/ -name "*.yaml" -exec kubeval {} \;

lint-ansible: ## Lint Ansible playbooks
	cd ansible && ansible-lint playbooks/main.yml

lint: lint-yaml lint-tf lint-ansible ## Run all linters

# ── Terraform ──────────────────────────────────────────────────────────────────
tf-init: ## Initialize Terraform (requires ENV=dev|staging|prod)
	@test -n "$(ENV)" || (echo "Usage: make tf-init ENV=dev" && exit 1)
	cd terraform && terraform init \
	  -backend-config=environments/$(ENV)/backend.tfvars 2>/dev/null || \
	  terraform init

tf-plan: ## Plan Terraform changes (requires ENV=dev|staging|prod)
	@test -n "$(ENV)" || (echo "Usage: make tf-plan ENV=dev" && exit 1)
	cd terraform && terraform plan \
	  -var-file=environments/$(ENV)/terraform.tfvars \
	  -out=tfplan

tf-apply: ## Apply Terraform plan (requires ENV=dev|staging|prod)
	@test -n "$(ENV)" || (echo "Usage: make tf-apply ENV=dev" && exit 1)
	cd terraform && terraform apply \
	  -var-file=environments/$(ENV)/terraform.tfvars \
	  -auto-approve

tf-destroy: ## Destroy Terraform resources (requires ENV=dev)
	@test "$(ENV)" = "dev" || (echo "Only allowed for ENV=dev" && exit 1)
	cd terraform && terraform destroy \
	  -var-file=environments/$(ENV)/terraform.tfvars

# ── Kubernetes ─────────────────────────────────────────────────────────────────
k8s-apply: ## Apply Kubernetes base manifests
	kubectl apply -k environment-configs/

k8s-diff: ## Show diff for Kubernetes manifests
	kubectl diff -k environment-configs/

k8s-delete: ## Delete Kubernetes resources
	kubectl delete -k environment-configs/

k8s-status: ## Show status of all fluxora resources
	kubectl get all -n fluxora

# ── Utilities ──────────────────────────────────────────────────────────────────
clean: ## Remove build artifacts and stopped containers
	docker compose $(COMPOSE_FILES) rm -f
	find . -name "*.tfplan" -delete
	find . -name ".terraform" -type d -exec rm -rf {} + 2>/dev/null || true

setup: ## First-time setup: copy .env.example to .env
	@test -f .env || cp .env.example .env
	@echo "✅ .env created. Please fill in your secret values before running 'make up'."
