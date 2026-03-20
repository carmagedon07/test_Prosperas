# test_Prosperas — Sistema de Procesamiento Asíncrono de Reportes

[![Deploy to AWS](https://github.com/carmagedon07/test_Prosperas/actions/workflows/deploy.yml/badge.svg)](https://github.com/carmagedon07/test_Prosperas/actions/workflows/deploy.yml)

**Prueba técnica · Prosperas · 2025**

> **URL de producción (Frontend):** [`https://d251z6g0rftk7e.cloudfront.net`](https://d251z6g0rftk7e.cloudfront.net)  
> **URL de producción (API):** `http://prosperas-alb-114099526.us-east-1.elb.amazonaws.com`

---

## Arquitectura

```
Usuario (browser)
    │
    ├──> CloudFront + S3  (React SPA)
    │
    └──> ALB ──> ECS Fargate · Backend (FastAPI :8000)
                     │                │
                     │                ├─> DynamoDB  prosperas-jobs
                     │                ├─> DynamoDB  prosperas-users
                     │                └─> SQS       prosperas-jobs-queue
                     │
                 ECS Fargate · Worker x2
                     │
                     ├─ consume SQS (long-polling)
                     ├─ procesa en thread paralelo (sleep 5-30s)
                     └─> DynamoDB  actualiza estado (PROCESSING → COMPLETED/FAILED)

                 SSM Parameter Store ──> JWT_SECRET (SecureString)
                 ECR ──> imágenes Docker backend + worker
```

**La decisión clave:** DynamoDB en lugar de RDS (sin VPC compleja, sin coste fijo) y dos workers ECS Fargate independientes para procesamiento paralelo real.

---

## Setup local (LocalStack)

```bash
# 1. Clonar
git clone https://github.com/carmagedon07/test_Prosperas.git
cd test_Prosperas

# 2. Variables de entorno
cp .env.example .env          # los valores por defecto funcionan sin cambios

# 3. Levantar todo (LocalStack + backend + 2 workers + frontend)
docker compose up --build

# La primera vez tarda ~2 min mientras LocalStack crea la tabla DynamoDB y la cola SQS

# 4. Acceder
#   Frontend:  http://localhost:3000
#   API Docs:  http://localhost:8000/docs

# 5. Registrar usuario y probar
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo", "password": "demo1234"}'
```

---

## Despliegue a producción

### 1. Infraestructura (Terraform)

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars   # completar jwt_secret
terraform init
terraform apply                                # ~3 min → crea todos los recursos AWS
terraform output                               # anotar URLs y credenciales CI/CD
```

### 2. Configurar GitHub Secrets

Con los outputs de Terraform, crear estos secrets en el repositorio:

`AWS_ACCESS_KEY_ID` · `AWS_SECRET_ACCESS_KEY` · `ECR_BACKEND_REPO` · `ECR_WORKER_REPO` · `REACT_APP_API_URL` · `S3_BUCKET` · `CLOUDFRONT_DISTRIBUTION_ID`

### 3. Primera imagen Docker

```bash
# Push inicial (el pipeline automático se activa en el siguiente push a main)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw ecr_backend_url | cut -d/ -f1)

docker build -t $(terraform output -raw ecr_backend_url):latest ./backend && \
  docker push $(terraform output -raw ecr_backend_url):latest

docker build -t $(terraform output -raw ecr_worker_url):latest -f worker/Dockerfile . && \
  docker push $(terraform output -raw ecr_worker_url):latest
```

### 4. Pipeline CI/CD

El pipeline `.github/workflows/deploy.yml` se activa automáticamente en cada `push` a `main`:

```
push a main → test (pytest) → build + push ECR → deploy ECS → build React → S3 sync → CloudFront invalidation
```

**Decisión de diseño del pipeline:** jobs secuenciales (test → build → deploy backend → deploy frontend) para garantizar que no se despliega frontend con un backend roto. Se podría paralelizar backend/frontend pero la ganancia es menor que el riesgo de inconsistencia.

---

## Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Documentación adicional

- [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) — Arquitectura completa, servicios AWS, guía de setup y despliegue
- [SKILL.md](SKILL.md) — Contexto para agentes de IA: patrones, comandos, errores comunes
- [AI_WORKFLOW.md](AI_WORKFLOW.md) — Evidencia de uso de GitHub Copilot
