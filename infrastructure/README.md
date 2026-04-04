# Fluxora Infrastructure

Financial-grade infrastructure for the Fluxora platform, compliant with **PCI DSS**, **GDPR**, and **SOC 2**.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Ingress / ALB                        │
└───────────────┬─────────────────────┬───────────────────┘
                │                     │
        ┌───────▼──────┐     ┌────────▼─────┐
        │   Frontend   │     │   Backend    │
        │   (Nginx)    │     │   (Node.js)  │
        └──────────────┘     └──────┬───────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐ ┌──────▼──────┐      │
            │   MySQL 8.0  │ │  Redis 7.2  │      │
            │  (StatefulSet│ │ (Deployment)│      │
            └──────────────┘ └─────────────┘      │
                                              Prometheus
                                              + Grafana
```

## Quick Start (Docker Compose)

```bash
# 1. Clone and set up environment
make setup          # copies .env.example → .env
nano .env           # fill in your secret values

# 2. Start all services
make up

# 3. Verify everything is running
make ps
make logs
```

Access:

- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:3000
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9091

## Directory Structure

```
├── ansible/                  # Server provisioning
│   ├── ansible.cfg
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── compliance/               # AWS compliance automation
│   ├── lambda/               # Compliance reporter Lambda
│   └── main.tf
├── config-management/        # Helm values
├── data-encryption/          # K8s encryption config
├── database/                 # Database cluster manifests
├── disaster-recovery/        # Backup & recovery
├── docker/                   # Docker support files
│   ├── grafana/
│   ├── mysql/
│   ├── nginx/
│   └── prometheus/
├── environment-configs/      # Kustomize configuration
├── gitops/                   # ArgoCD applications
├── kubernetes/               # K8s base manifests
│   ├── base/
│   └── environments/
├── kubernetes-scaling/       # HPA, service mesh, registry
├── monitoring/               # Prometheus, Alertmanager, ELK, SIEM
├── secrets-management/       # AWS Secrets Manager Terraform
├── storage/                  # Storage class definitions
├── terraform/                # AWS infrastructure
│   ├── environments/
│   └── modules/
├── Dockerfile.backend        # Backend image
├── Dockerfile.frontend       # Frontend image
├── docker-compose.yml        # Development stack
├── docker-compose.prod.yml   # Production overrides
├── docker-compose.test.yml   # Integration test stack
├── Makefile                  # Convenience commands
└── .env.example              # Environment template
```

## Kubernetes Deployment

```bash
# Apply base manifests
make k8s-apply

# Check status
make k8s-status

# Show diff before applying
make k8s-diff
```

## Terraform (AWS)

```bash
# Initialize and plan for dev
make tf-init ENV=dev
make tf-plan ENV=dev
make tf-apply ENV=dev
```

## Environment Variables

| Variable                 | Description                    | Required |
| ------------------------ | ------------------------------ | -------- |
| `MYSQL_ROOT_PASSWORD`    | MySQL root password            | ✅       |
| `MYSQL_PASSWORD`         | MySQL app user password        | ✅       |
| `JWT_SECRET`             | JWT signing secret (≥32 chars) | ✅       |
| `ENCRYPTION_KEY`         | AES encryption key (32 bytes)  | ✅       |
| `REDIS_PASSWORD`         | Redis auth password            | ✅       |
| `API_KEY`                | Application API key            | ✅       |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password         | ✅       |

## Compliance

This infrastructure is designed to meet:

- **PCI DSS** – Encryption at rest & in transit, audit logging, network segmentation, access controls
- **GDPR** – Data minimisation, right to erasure support, audit trails, retention policies
- **SOC 2** – Availability, confidentiality, security monitoring, change management

## Security Notes

- ⚠️ **Never commit `.env` files** – use `.env.example` as template
- ⚠️ **Never commit `terraform.tfvars`** – only `*.tfvars.example`
- ⚠️ **Never commit `kubernetes/base/app-secrets.yaml`** – use external secrets
- All secrets in production should use **AWS Secrets Manager** or **Vault**
- Database passwords in `terraform.tfvars` must be set via environment variable: `TF_VAR_db_password`
