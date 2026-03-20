# SKILL.md — Contexto de IA para el Proyecto Prosperas

> Este archivo está diseñado para ser inyectado como contexto en un agente de IA.
> La IA que lo lea debe poder operar sobre el código sin necesidad de leer cada archivo.

---

## ¿Qué hace este sistema?

Sistema de procesamiento asíncrono de reportes. Los usuarios piden reportes a través de un formulario React → el backend FastAPI crea el job y lo manda a una cola SQS → dos workers en paralelo consumen la cola, simulan procesamiento (sleep 5-30s aleatorio), y marcan el job como COMPLETED o FAILED → el frontend muestra el estado en tiempo real via polling cada 5 segundos.

**Stack:** Python 3.11 + FastAPI (backend) · React 18 (frontend) · AWS SQS (mensajería) · AWS DynamoDB (persistencia) · AWS ECS Fargate (hosting) · Terraform (IaC) · GitHub Actions (CI/CD).

---

## Mapa del repositorio

```
test_Prosperas/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── main.py             # FastAPI app, registro de routers
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py     # POST /auth/login, POST /auth/register
│   │   │   │   ├── jobs.py     # POST /jobs, GET /jobs, GET /jobs/{id}
│   │   │   │   └── health.py   # GET /health (ALB health check)
│   │   │   ├── dependencies.py # get_current_user (JWT decode)
│   │   │   ├── exception_handlers.py # handlers globales de errores
│   │   │   └── schemas/
│   │   │       └── job.py      # Pydantic v2 schemas (JobCreate, JobResponse)
│   │   ├── application/
│   │   │   ├── interfaces/
│   │   │   │   └── job_repository.py  # Interfaz abstracta (ABC)
│   │   │   └── use_cases/
│   │   │       ├── create_job.py       # Crea job + publica en SQS
│   │   │       ├── get_job.py          # Lee job por ID
│   │   │       ├── list_jobs.py        # Lista jobs de un usuario (paginado)
│   │   │       └── update_job_status.py # Cambia estado del job
│   │   ├── core/
│   │   │   └── security.py     # create_access_token, verify_password, get_password_hash
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── job.py      # Dataclass Job (job_id, user_id, status, ...)
│   │   │   └── enums/
│   │   │       └── job_status.py # JobStatus enum: PENDING, PROCESSING, COMPLETED, FAILED
│   │   └── infrastructure/
│   │       ├── db/             # (legacy SQLite — no usado en producción)
│   │       └── repositories/
│   │           ├── job_repository_dynamodb.py   # CRUD de jobs en DynamoDB
│   │           └── user_repository_dynamodb.py  # CRUD de usuarios en DynamoDB
│   ├── tests/                  # pytest — unit tests con mocks
│   ├── requirements.txt
│   └── Dockerfile
│
├── worker/
│   ├── main.py                 # SQS consumer; procesa mensajes en threads paralelos
│   └── Dockerfile
│
├── frontend/                   # React 18
│   └── src/
│       ├── App.js
│       ├── components/
│       │   ├── JobForm.js      # Formulario de solicitud de reporte
│       │   ├── JobList.js      # Lista paginada de jobs
│       │   ├── JobItem.js      # Fila individual (badge de estado)
│       │   ├── JobStatus.js    # Badge de color por estado
│       │   └── Navbar.js
│       ├── context/
│       │   └── AuthContext.js  # Context de autenticación (JWT en localStorage)
│       ├── hooks/
│       │   └── usePolling.js   # Hook para polling periódico
│       ├── pages/
│       │   ├── Dashboard.js    # Página principal (JobForm + JobList)
│       │   └── LoginPage.js    # Login + Register (tabs)
│       └── services/
│           └── api.js          # Funciones fetch hacia el backend
│
├── infra/                      # Terraform — infraestructura AWS
│   ├── main.tf                 # Provider + data sources (VPC, subnets, account)
│   ├── variables.tf            # Variables de entrada
│   ├── locals.tf               # Tags comunes
│   ├── outputs.tf              # Outputs (URLs, ARNs para GitHub Secrets)
│   ├── ecr.tf                  # ECR repos (backend, worker)
│   ├── dynamodb.tf             # Tablas DynamoDB + GSI
│   ├── sqs.tf                  # SQS jobs-queue + jobs-dlq
│   ├── secrets.tf              # SSM Parameter Store para JWT_SECRET
│   ├── iam.tf                  # Roles ECS + usuario CI/CD
│   ├── security_groups.tf      # SGs para ALB, backend, worker
│   ├── alb.tf                  # Application Load Balancer
│   ├── ecs.tf                  # Cluster ECS + task defs + servicios
│   └── s3_cloudfront.tf        # S3 frontend + CloudFront
│
├── .github/workflows/
│   └── deploy.yml              # CI/CD: test → build ECR → deploy ECS → deploy S3/CF
│
├── docker-compose.yml          # Entorno local completo (LocalStack + todos los servicios)
├── .env.example                # Template de variables de entorno
├── TECHNICAL_DOCS.md           # Documentación técnica completa
├── SKILL.md                    # Este archivo
└── AI_WORKFLOW.md              # Evidencia de uso de IA
```

---

## Patrones del proyecto

### ¿Cómo agregar una nueva ruta en el backend?

1. Crear o editar un archivo en `backend/app/api/routes/`
2. Definir el router: `router = APIRouter(prefix="/mi-recurso", tags=["mi-recurso"])`
3. Añadir dependencia de autenticación si se necesita: `current_user: str = Depends(get_current_user)`
4. Registrar en `backend/app/main.py`: `app.include_router(mi_router.router)`
5. Si requiere validación, añadir schema Pydantic en `backend/app/api/schemas/`

**Ejemplo — GET /stats:**
```python
# backend/app/api/routes/stats.py
from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("")
def get_stats(current_user: str = Depends(get_current_user)):
    return {"user": current_user, "total_jobs": 0}
```
Y en `main.py`: `from .api.routes import stats` + `app.include_router(stats.router)`

---

### ¿Cómo publicar un nuevo tipo de mensaje a SQS?

En `create_job.py` (use case), se usa `boto3.client("sqs")` y `sqs.send_message`. El mismo patrón vale para cualquier evento:

```python
import boto3, os, json

sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"),
                   endpoint_url=os.getenv("SQS_ENDPOINT") or None)

sqs.send_message(
    QueueUrl=os.getenv("SQS_QUEUE_URL") or sqs.get_queue_url(
        QueueName=os.getenv("SQS_QUEUE_NAME", "jobs-queue"))["QueueUrl"],
    MessageBody=json.dumps({"job_id": str(job_id), "event": "nuevo_evento"})
)
```

---

### ¿Cómo leer el estado de un job?

```python
# Usar el use case directamente (inyección de dependencia)
from app.application.use_cases.get_job import GetJobUseCase
from app.infrastructure.repositories.job_repository_dynamodb import JobRepositoryDynamoDB

repo = JobRepositoryDynamoDB()
use_case = GetJobUseCase(repo)
job = use_case.execute(job_id=UUID("..."))
print(job.status.value)  # "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED"
```

---

### ¿Cómo agrega un nuevo tipo de reporte al sistema?

1. **Enum** (si se necesita validación estricta): añadir valor en `backend/app/domain/enums/job_status.py` o crear `report_type_enum.py`.
2. **Schema**: añadir campo o regex en `backend/app/api/schemas/job.py` (Pydantic v2).
3. **Worker**: en `worker/main.py` → función `process_job` → añadir lógica condicional según `report_type`:
   ```python
   data = json.loads(body)
   report_type = data.get("report_type", "generic")
   if report_type == "financial":
       duration = random.uniform(15, 30)  # más pesado
   else:
       duration = random.uniform(5, 15)
   ```
4. **Frontend**: en `JobForm.js` → añadir opción al `<select>` de `report_type`.
5. No se requieren migraciones de base de datos (DynamoDB es schema-less).

---

## Comandos frecuentes

### Levantar entorno local

```bash
docker compose up --build          # Primera vez (construye imágenes)
docker compose up                  # Siguientes veces
docker compose down -v             # Apagar y borrar volúmenes
```

### Correr tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
python -m pytest tests/ --cov=app  # Con cobertura
```

### Ver logs en local

```bash
docker compose logs backend -f     # Logs del backend
docker compose logs worker -f      # Logs del worker #1
docker compose logs worker2 -f     # Logs del worker #2
docker compose logs localstack -f  # Logs de localstack
```

### Deploy manual a AWS

```bash
# 1. Aplicar infra (primera vez o si hay cambios en infra/)
cd infra && terraform apply

# 2. Push imagen backend manual (si no usas el pipeline)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ECR_URL>
docker build -t <ECR_BACKEND_URL>:latest ./backend
docker push <ECR_BACKEND_URL>:latest

# 3. Forzar nuevo deployment
aws ecs update-service --cluster prosperas-cluster \
  --service prosperas-backend --force-new-deployment

# 4. Ver logs de ECS en CloudWatch
aws logs tail /ecs/prosperas/backend --follow
aws logs tail /ecs/prosperas/worker --follow
```

### Ver logs en producción (AWS)

```bash
aws logs tail /ecs/prosperas/backend --follow --region us-east-1
aws logs tail /ecs/prosperas/worker  --follow --region us-east-1
```

---

## Errores comunes y cómo resolverlos

| Error | Causa | Solución |
|---|---|---|
| `Connection refused localhost:4566` | LocalStack no arrancó aún | Esperar ~30s, verificar `docker compose logs localstack` |
| `ResourceNotFoundException: jobs table` | La tabla DynamoDB no fue creada | Correr `docker compose run --rm init-aws` o revisar logs del servicio `init-aws` |
| `ExpiredSignatureError` | Token JWT vencido | Hacer login de nuevo; el token dura 60 minutos |
| `Task definition inactive` | ECS no tiene imagen en ECR | Hacer push de imágenes a ECR antes del primer `terraform apply` o del deploy |
| `Health check failing` | `GET /health` devuelve error | Verificar que el backend arrancó correctamente: `docker compose logs backend` |
| `SQS Queue does not exist` | Queue name incorrecto | Verificar `SQS_QUEUE_NAME` en `.env` (local: `jobs-queue`, prod: `prosperas-jobs-queue`) |
| `403 Forbidden from CloudFront` | Bucket policy o OAC mal configurado | Verificar que `terraform apply` completó sin errores en `s3_cloudfront.tf` |
| Worker no procesa mensajes | `SQS_ENDPOINT` apunta a localstack en producción | Asegurarse de que `SQS_ENDPOINT` esté vacío en env vars de ECS |

---

## Arquitectura de seguridad

- **JWT** firmado con HS256, secreto en SSM Parameter Store (SecureString cifrado con KMS).
- **Contraseñas** hasheadas con bcrypt (12 rondas).
- **IAM least-privilege**: el usuario CI/CD sólo puede hacer push a ECR, actualizar ECS y hacer sync a S3/$CloudFront. Los workers sólo pueden leer/escribir las tablas DynamoDB específicas y la cola SQS específica.
- **Red**: workers sin acceso a internet de entrada (sólo egress), backend sólo accesible vía ALB.
- **Secretos**: nunca en imágenes Docker ni en variables de entorno de texto plano en ECS.

---

## DLQ — Qué pasa cuando un job falla repetidamente

Si el worker falla al procesar un mensaje 3 veces (`maxReceiveCount=3`), SQS mueve el mensaje a `prosperas-jobs-dlq` automáticamente. La retención es de 14 días. 

Para redriving (reenviar mensajes del DLQ a la cola principal):
```bash
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:<ACCOUNT>:prosperas-jobs-dlq \
  --destination-arn arn:aws:sqs:us-east-1:<ACCOUNT>:prosperas-jobs-queue
```
