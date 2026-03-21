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

## Referencia de variables de entorno

Todas las variables de entorno usadas en el sistema. Para desarrollo local, usar valores con `_ENDPOINT` apuntando a LocalStack. Para producción AWS, eliminar `*_ENDPOINT` y dejar que boto3 use IAM roles.

### Backend (FastAPI)

| Variable | Requerida | Default | Descripción | Local | Producción |
|----------|-----------|---------|-------------|-------|------------|
| `BACKEND_PORT` | Sí | `8000` | Puerto HTTP del servidor FastAPI | `8000` | `8000` |
| `JWT_SECRET` | Sí | `super-secret-key...` | Secreto HS256 para firmar tokens JWT (min 32 chars) | Cualquier valor largo | Desde SSM Parameter con KMS |
| `JWT_EXPIRY_MINUTES` | Sí | `60` | Tiempo de vida del JWT en minutos | `60` | `60` o más |
| `AWS_REGION` | Sí | `us-east-1` | Región AWS de recursos | `us-east-1` | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Condicional | `test` | Credenciales AWS | `test` (LocalStack) | Omitir (usa ECS Task Role) |
| `AWS_SECRET_ACCESS_KEY` | Condicional | `test` | Credenciales AWS | `test` (LocalStack) | Omitir (usa ECS Task Role) |
| `SQS_QUEUE_NAME` | Sí | `jobs-queue` | Nombre de la cola SQS | `jobs-queue` | `prospera-jobs-queue` |
| `SQS_QUEUE_URL` | No | (calculado) | URL completa de la cola (opcional, se calcula automáticamente) | — | — |
| `SQS_ENDPOINT` | Solo local | `http://localstack:4566` | **Solo para LocalStack**. Si existe, apunta a este endpoint. Si no existe o vacío → usa AWS real | `http://localstack:4566` | **ELIMINAR** |
| `DYNAMODB_TABLE_NAME` | Sí | `jobs` | Nombre de la tabla de jobs | `jobs` | `prospera-jobs` |
| `DYNAMODB_ENDPOINT` | Solo local | `http://localstack:4566` | **Solo para LocalStack**. Si existe, apunta a este endpoint. | `http://localstack:4566` | **ELIMINAR** |
| `USERS_TABLE_NAME` | Sí | `users` | Nombre de la tabla de usuarios DynamoDB | `users` | `prospera-users` |
| `FRONTEND_URL` | Sí | `http://localhost:3000` | URL del frontend para validación CORS | `http://localhost:3000` | `https://*.cloudfront.net` |
| `LOG_FORMAT` | No | `text` | Formato de logs: `text` o `json` | `text` | `json` (para CloudWatch) |
| `ENVIRONMENT` | No | `development` | Entorno de ejecución (para logs) | `development` | `production` |

### Worker (SQS Consumer)

| Variable | Requerida | Default | Descripción | Local | Producción |
|----------|-----------|---------|-------------|-------|------------|
| `AWS_REGION` | Sí | `us-east-1` | Región AWS | `us-east-1` | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Condicional | `test` | Credenciales AWS | `test` | Omitir (ECS Task Role) |
| `AWS_SECRET_ACCESS_KEY` | Condicional | `test` | Credenciales AWS | `test` | Omitir (ECS Task Role) |
| `SQS_QUEUE_NAME` | Sí | `test-queue` | Nombre de la cola SQS a consumir | `jobs-queue` | `prospera-jobs-queue` |
| `SQS_ENDPOINT` | Solo local | — | Endpoint de SQS para LocalStack | `http://localstack:4566` | **ELIMINAR** |
| `DYNAMODB_TABLE_NAME` | Sí | `jobs` | Tabla de jobs (para actualizar estado) | `jobs` | `prospera-jobs` |
| `DYNAMODB_ENDPOINT` | Solo local | — | Endpoint DynamoDB para LocalStack | `http://localstack:4566` | **ELIMINAR** |
| `JOBS_TABLE_NAME` | Alternativa | `jobs` | Alias para `DYNAMODB_TABLE_NAME` (se usa si está definida) | `jobs` | `prospera-jobs` |
| `WORKER_INSTANCE_ID` | No | `default` | ID del worker (para logs de debugging) | `worker-1`, `worker-2` | `task-${ECS_TASK_ID}` |
| `WORKER_CONCURRENCY` | No | `2` (en código) | Número de threads concurrentes (hardcoded en código como `max_workers=2`) | `2` | `4` (via Terraform) |

**Nota sobre concurrencia:** El worker usa `ThreadPoolExecutor(max_workers=2)` en código local. En producción, Terraform inyecta `WORKER_CONCURRENCY=4`, pero el código debe modificarse para leerla.

### Frontend (React)

| Variable | Requerida | Default | Descripción | Local | Producción |
|----------|-----------|---------|-------------|-------|------------|
| `REACT_APP_API_URL` | Sí | `http://localhost:8000/api` | URL base del backend API (sin `/api` si el backend ya lo incluye) | `http://localhost:8000/api` | `https://alb-dns-name.region.elb.amazonaws.com/api` |

**Importante:** Variables de React deben empezar con `REACT_APP_` y estar definidas en build-time (no runtime). Se inyectan en `Dockerfile` con `ARG` y luego `ENV`.

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

## Convenciones de código

El proyecto sigue convenciones específicas para mantener consistencia. Estas deben respetarse al agregar o modificar código.

### Nomenclatura

#### Python (Backend / Worker)
- **Archivos:** `snake_case.py` — ejemplos: `job_repository_dynamodb.py`, `create_job.py`
- **Clases:** `PascalCase` — ejemplos: `JobRepository`, `CreateJobUseCase`, `JobStatus`
- **Funciones/métodos:** `snake_case` — ejemplos: `create_job()`, `get_current_user()`, `verify_token()`
- **Constantes:** `UPPER_SNAKE_CASE` — ejemplos: `JWT_SECRET`, `AWS_REGION`, `SQS_QUEUE_NAME`
- **Variables privadas:** prefijo `_` — ejemplo: `_to_domain()` en repositorios
- **Parámetros opcionales:** con valor por defecto explícito — ejemplo: `page: int = 1, page_size: int = 20`

#### JavaScript/React (Frontend)
- **Archivos componentes:** `PascalCase.js` — ejemplos: `JobList.js`, `Dashboard.js`, `AuthContext.js`
- **Archivos utilidades:** `camelCase.js` — ejemplos: `api.js`, `usePolling.js`
- **Componentes:** `PascalCase` — ejemplos: `JobStatus`, `Navbar`, `LoginPage`
- **Funciones/hooks:** `camelCase` — ejemplos: `createJob()`, `usePolling()`, `getJobs()`
- **Constantes:** `UPPER_SNAKE_CASE` — ejemplo: `API_URL`
- **Props:** `camelCase` — ejemplos: `jobId`, `onSubmit`, `isLoading`

#### Terraform (Infra)
- **Archivos:** `snake_case.tf` — ejemplos: `security_groups.tf`, `ecs_backend.tf`
- **Recursos:** `snake_case` con prefijo de proyecto — ejemplos: `prospera-backend`, `prospera-jobs-queue`
- **Variables:** `snake_case` — ejemplos: `aws_region`, `backend_cpu`, `image_tag`

### Formatos de datos

| Concepto | Formato | Ejemplo | Dónde se aplica |
|----------|---------|---------|-----------------|
| **Job ID** | UUID v4 (string)  | `"550e8400-e29b-41d4-a716-446655440000"` | Entity, DynamoDB, API responses |
| **User ID** | String alfanumérico, 3-50 chars | `"usuario123"`, `"superadmin"` | Registro, JWT payload, DynamoDB PK |
| **Fechas (timestamps)** | ISO 8601 (UTC) | `"2026-03-21T14:30:00.123456"` | `created_at`, `updated_at` en DynamoDB |
| **Date range** | String con formato libre | `"2026-01-01 to 2026-01-31"` | Campo `date_range` en Job |
| **Estado de job** | Enum string uppercase | `"PENDING"`, `"PROCESSING"`, `"COMPLETED"`, `"FAILED"` | JobStatus enum |
| **Role usuario** | String lowercase | `"user"`, `"admin"` | JWT payload, tabla `users` |
| **Token JWT** | JWT firmado HS256 | `"eyJhbGciOiJIUzI1NiIsInR5..."` | Header `Authorization: Bearer <token>` |
| **Result URL** | String URL | `"https://dummy.result/550e8400-..."` | Campo `result_url` cuando `COMPLETED` |

### Respuestas de error

Todas las respuestas de error HTTP siguen este formato estandarizado (definido en `exception_handlers.py`):

```json
{
  "detail": "Mensaje de error legible"
}
```

**Códigos de estado comunes:**
- `400` — Bad Request (validación de entrada falló)
- `401` — Unauthorized (token inválido, expirado o ausente)
- `403` — Forbidden (sin permisos suficientes: admin required)
- `404` — Not Found (job no existe o pertenece a otro usuario)
- `409` — Conflict (usuario ya existe en registro)
- `422` — Unprocessable Entity (validación Pydantic falló — incluye campo `body`)
- `500` — Internal Server Error (error inesperado del servidor)
- `503` — Service Unavailable (health check falló, DynamoDB o SQS no disponible)

### Estructura de casos de uso (Use Cases)

Todos los casos de uso siguen este patrón (Clean Architecture):

```python
from ...application.interfaces.job_repository import JobRepository

class MiUseCaseUseCase:
    def __init__(self, repository: JobRepository):
        self.repository = repository
    
    def execute(self, parametro1: tipo, parametro2: tipo) -> TipoRetorno:
        # Lógica del caso de uso
        # Validaciones de negocio
        # Llamadas al repositorio
        return resultado
```

**Inyección de dependencias** en rutas:
```python
job_repository = JobRepositoryDynamoDB()
mi_use_case = MiUseCaseUseCase(job_repository)
resultado = mi_use_case.execute(param1, param2)
```

### Logging

- **Backend:** usa `logging_config.py` → logs estructurados con `extra={}` dict
- **Worker:** usa `print()` con prefijo `[{instance_id}]` para identificar worker
- **Formato local:** texto legible
- **Formato producción:** JSON para CloudWatch Logs Insights

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

## Contratos de API

Todos los endpoints REST del backend. Base URL local: `http://localhost:8000`, producción: `https://<ALB-DNS>/`.

### `POST /api/auth/register`

Registro de nuevo usuario. **No requiere autenticación.** El rol siempre es `"user"`.

**Request:**
```json
{
  "user_id": "usuario123",
  "password": "mipassword"
}
```

**Validación:**
- `user_id`: 3-50 caracteres
- `password`: mínimo 6 caracteres

**Response 201 Created:**
```json
{
  "user_id": "usuario123",
  "role": "user",
  "message": "Usuario creado exitosamente"
}
```

**Errores:**
- `409 Conflict` — usuario ya existe

---

### `POST /api/auth/login`

Autenticación de usuario existente. **No requiere autenticación.**

**Request:**
```json
{
  "user_id": "usuario123",
  "password": "mipassword"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "user",
  "token_type": "bearer"
}
```

**Errores:**
- `401 Unauthorized` — credenciales inválidas

**Nota:** El token expira según `JWT_EXPIRY_MINUTES` (default 60 min). El rol `"admin"` se asigna automáticamente si `user_id == "superadmin"` (hardcoded en `security.py`).

---

### `POST /api/jobs`

Crear un nuevo job de reporte. **Requiere autenticación** (`Bearer token`).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "report_type": "ventas",
  "date_range": "2026-01-01 to 2026-01-31",
  "format": "PDF"
}
```

**Response 201 Created:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "usuario123",
  "status": "PENDING",
  "report_type": "ventas",
  "date_range": "2026-01-01 to 2026-01-31",
  "format": "PDF",
  "created_at": "2026-03-21T14:30:00.123456",
  "updated_at": "2026-03-21T14:30:00.123456",
  "result_url": null
}
```

**Errores:**
- `401 Unauthorized` — token inválido o ausente
- `422 Unprocessable Entity` — validación de campos falló

**Flujo:** El backend crea el job en DynamoDB con estado `PENDING` y publica mensaje en SQS. El worker lo consume y procesa.

---

### `GET /api/jobs`

Listar jobs del usuario autenticado (paginado). **Requiere autenticación.**

**Headers:**
```
Authorization: Bearer <token>
```

**Query parameters:**
- `page` (opcional): número de página, base 1. Default: `1`. Mínimo: `1`.
- `page_size` (opcional): items por página. Default: `20`. Rango: `1-100`.

**Ejemplo:** `GET /api/jobs?page=2&page_size=10`

**Response 200 OK:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "usuario123",
      "status": "COMPLETED",
      "report_type": "ventas",
      "date_range": "2026-01-01 to 2026-01-31",
      "format": "PDF",
      "created_at": "2026-03-21T14:30:00.123456",
      "updated_at": "2026-03-21T14:35:12.789012",
      "result_url": "https://dummy.result/550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "total": 42,
  "page": 2,
  "page_size": 10,
  "total_pages": 5
}
```

**Errores:**
- `401 Unauthorized` — token inválido o ausente

**Nota:** Los jobs se ordenan por `created_at` descendente (más recientes primero). Solo se retornan jobs del usuario autenticado (filtrado en DynamoDB con GSI `UserIdIndex`).

---

### `GET /api/jobs/{job_id}`

Obtener un job específico por ID. **Requiere autenticación.** Solo puede acceder el dueño del job.

**Headers:**
```
Authorization: Bearer <token>
```

**Path parameters:**
- `job_id`: UUID v4

**Ejemplo:** `GET /api/jobs/550e8400-e29b-41d4-a716-446655440000`

**Response 200 OK:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "usuario123",
  "status": "PROCESSING",
  "report_type": "ventas",
  "date_range": "2026-01-01 to 2026-01-31",
  "format": "PDF",
  "created_at": "2026-03-21T14:30:00.123456",
  "updated_at": "2026-03-21T14:32:05.123456",
  "result_url": null
}
```

**Errores:**
- `401 Unauthorized` — token inválido o ausente
- `404 Not Found` — job no existe o pertenece a otro usuario

---

### `DELETE /api/jobs`

Eliminar todos los jobs de la tabla DynamoDB. **Requiere rol admin.** Endpoint de administración.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "message": "Successfully deleted 42 jobs",
  "count": 42
}
```

**Errores:**
- `401 Unauthorized` — token inválido o ausente
- `403 Forbidden` — usuario no tiene rol `admin`

**Nota:** Solo el usuario `superadmin` tiene rol admin (hardcoded en `security.py`). Este endpoint es para limpiar datos de prueba.

---

### `GET /health`

Health check para ALB y monitoreo. **No requiere autenticación.**

**Response 200 OK (healthy):**
```json
{
  "service": "backend",
  "status": "healthy",
  "checks": {
    "dynamodb": {
      "status": "healthy",
      "table": "jobs",
      "item_count": 42
    },
    "sqs": {
      "status": "healthy",
      "queue": "jobs-queue",
      "messages_available": "3",
      "messages_in_flight": "2"
    }
  }
}
```

**Response 503 Service Unavailable (degraded):**
```json
{
  "service": "backend",
  "status": "degraded",
  "checks": {
    "dynamodb": {
      "status": "unhealthy",
      "error": "ResourceNotFoundException: Table 'jobs' not found"
    },
    "sqs": {
      "status": "healthy",
      "queue": "jobs-queue",
      "messages_available": "0",
      "messages_in_flight": "0"
    }
  }
}
```

**Nota:** ALB marca el target como unhealthy si recibe 503. El backend responde 503 si alguno de los checks (DynamoDB o SQS) falla.

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

---

## Código frágil — No tocar sin discusión

Secciones del código que son legacy, tienen decisiones deliberadas, o son particularmente sensibles. Modificarlas puede romper funcionalidad o tiene implicaciones de arquitectura.

### 1. Carpeta `backend/app/infrastructure/db/` — Legacy SQLite (NO USADO EN PRODUCCIÓN)

**Ubicación:** `backend/app/infrastructure/db/` — archivos: `models.py`, `session.py`, `init_db.py`

**Qué es:** Implementación original con SQLAlchemy + SQLite. Fue reemplazada por DynamoDB (`job_repository_dynamodb.py`).

**Estado:** 
- ⚠️ **Código muerto** — no se usa en ningún entorno (ni local ni producción)
- Se mantiene por historial y referencia de migración
- Los modelos SQLAlchemy (`JobModel`) NO están sincronizados con la entidad de dominio actual

**Riesgos si se toca:**
- Ninguno (no se ejecuta), pero puede confundir a futuros desarrolladores
- Si se elimina, perder referencia de cómo era la implementación original pre-DynamoDB

**Recomendación:** Dejar intacto. Si se quiere limpiar, mover a carpeta `backend/legacy/` con un README explicativo.

---

### 2. Hardcoded admin role — `user_id == "superadmin"` 

**Ubicación:** `backend/app/core/security.py` línea 9

```python
role = "admin" if user_id == "superadmin" else "user"
```

**Qué es:** Decisión deliberada para simplificar. No hay tabla de roles ni gestión de permisos compleja. El único admin es el usuario con `user_id` exactamente igual a `"superadmin"`.

**Riesgos si se cambia:**
- Rompe el endpoint `DELETE /api/jobs` (requiere admin)
- Rompe tests que asumen este comportamiento
- Si se quiere multi-admin, requiere diseño de tabla de roles en DynamoDB + migración de lógica de autenticación

**Recomendación:** Si se necesita multi-admin, crear un atributo `role` en la tabla `users` y leerlo en `authenticate()` del repositorio, luego incluir `role` en el JWT payload.

---

### 3. Concurrencia del worker — `max_workers=2` hardcoded

**Ubicación:** `worker/main.py` línea 104

```python
with ThreadPoolExecutor(max_workers=2) as executor:
```

**Qué es:** Límite de concurrencia por instancia de worker. Con 2 workers (ECS tasks) × 2 threads = 4 jobs simultáneos.

**Estado:**
- En Terraform se inyecta `WORKER_CONCURRENCY=4`, pero el código **no la lee**
- Valor hardcoded intencionalmente para prevenir saturación de recursos (cada job duerme 60-90s aleatorios)

**Riesgos si se cambia:**
- Aumentar a >4 threads puede saturar DynamoDB (no hay rate limiting implementado)
- Reducir a 1 thread reduce throughput innecesariamente

**Recomendación:** Si se quiere parametrizar, leer `os.getenv("WORKER_CONCURRENCY", "2")` y convertir a int. Validar max 10 threads por worker.

---

### 4. Duración aleatoria de jobs — `random.uniform(60, 90)`

**Ubicación:** `worker/main.py` línea 80

```python
duration = random.uniform(60, 90)
```

**Qué es:** Simulación de procesamiento real. Los jobs tardan entre 60-90 segundos (antes era 5-30s). Es deliberado para testear polling, timeouts SQS (180s), y concurrencia.

**Riesgos si se cambia:**
- Reducir a <30s hace que los jobs terminen muy rápido (polling del frontend los vería casi siempre COMPLETED)
- Aumentar a >150s requiere aumentar `VisibilityTimeout` en SQS (actualmente 180s) para evitar mensajes duplicados

**Recomendación:** Si se cambia, asegurar que `VisibilityTimeout` (línea 103 del worker) sea al menos `duration_max + 30s`.

---

### 5. CORS `allow_origins=["*"]` en desarrollo

**Ubicación:** `backend/app/main.py` línea 24

```python
allow_origins=["*"],  # Cambia esto a los orígenes permitidos en producción
```

**Qué es:** CORS abierto para desarrollo local. En producción debería restringirse a `FRONTEND_URL`.

**Estado:** Comentario indica que es temporal, pero no se cambió.

**Riesgos:**
- Producción actual permite CORS desde cualquier origen (vulnerabilidad de seguridad: CSRF)
- Si se restringe sin configurar correctamente `FRONTEND_URL`, el frontend en CloudFront no podrá llamar al backend

**Recomendación:** Cambiar a:
```python
allow_origins=[os.getenv("FRONTEND_URL", "*").split(",")],
```
Y en producción inyectar `FRONTEND_URL=https://d1234567890.cloudfront.net`.

---

### 6. DynamoDB `item_count` en health check — puede estar desactualizado

**Ubicación:** `backend/app/api/routes/health.py` línea 48

```python
"item_count": table.item_count if hasattr(table, 'item_count') else "N/A"
```

**Qué es:** `table.item_count` es metadata que DynamoDB actualiza cada ~6 horas. No es tiempo real.

**Riesgos:**
- Si se usa para decisiones críticas (ej. alertas cuando `item_count > 1000`), estará desfasado
- Es solo informativo para debugging

**Recomendación:** Dejar como está, pero no confiar en este valor para lógica de negocio. Si se necesita count preciso, hacer un `Scan` (costoso).

---

## Deuda técnica y limitaciones conocidas

Funcionalidades incompletas, hardcodeos, y mejoras pendientes identificadas en el código.

### 1. Worker no lee `WORKER_CONCURRENCY` de env var

**Ubicación:** `worker/main.py` línea 104

**Problema:** Terraform inyecta `WORKER_CONCURRENCY=4` pero el código usa `max_workers=2` hardcoded.

**Impacto:** En producción, cada worker solo procesa 2 jobs concurrentes en lugar de 4.

**Solución propuesta:**
```python
max_workers = int(os.getenv("WORKER_CONCURRENCY", "2"))
with ThreadPoolExecutor(max_workers=max_workers) as executor:
```

---

### 2. Sin paginación eficiente en DynamoDB (scan completo + slice en memoria)

**Ubicación:** `backend/app/infrastructure/repositories/job_repository_dynamodb.py` líneas 56-72

**Problema:** `list_jobs()` hace query de TODOS los items del usuario con `UserIdIndex`, los carga en memoria, y luego hace slicing para paginación:
```python
all_items: List[dict] = []
while True:
    response = self.table.query(**query_kwargs)
    all_items.extend(response.get('Items', []))
    # ... pagination loop
all_items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
page_items = all_items[offset: offset + page_size]  # slice en memoria
```

**Impacto:** 
- Si un usuario tiene 10,000 jobs, se cargan todos en memoria aunque solo se retornen 20
- Alto consumo de RCUs (DynamoDB Read Capacity Units)

**Solución propuesta:** Usar `LastEvaluatedKey` de DynamoDB para paginación nativa (requiere cambio de API a cursor-based pagination en lugar de page numbers).

---

### 3. Sin manejo de DLQ — mensajes en DLQ se pierden

**Ubicación:** Arquitectura SQS — `infra/sqs.tf`

**Problema:** Los mensajes que fallan 3 veces van a `prosperas-jobs-dlq` pero no hay:
- Monitoreo/alertas cuando hay mensajes en DLQ
- Proceso automático de retry o análisis de errores
- Dashboard para ver qué jobs están en DLQ

**Impacto:** Jobs fallidos silenciosamente se pierden hasta que alguien revise manualmente el DLQ.

**Solución propuesta:**
- CloudWatch alarm cuando `ApproximateNumberOfMessagesVisible` en DLQ > 0
- Lambda que se dispara con eventos de DLQ y envía notificación (SNS/email)
- Script de redrive manual: `aws sqs start-message-move-task` (ya documentado en SKILL.md)

---

### 4. Logs no estructurados en worker

**Ubicación:** `worker/main.py` — todo el archivo

**Problema:** Worker usa `print()` en lugar de `logging` con formato estructurado. Dificulta búsquedas en CloudWatch Logs Insights.

**Impacto:** 
- No se puede filtrar por `job_id` o `user_id` en CloudWatch fácilmente
- Queries Insights requieren regex complejos

**Solución propuesta:** Migrar a `logging` con `JSONFormatter` (similar a backend) y logs estructurados.

---

### 5. Sin rate limiting ni throttling en API

**Ubicación:** Backend — no existe middleware de rate limiting

**Problema:** Un usuario puede crear miles de jobs en segundos (sin límite de requests).

**Impacto:**
- Posible saturación de SQS
- Costos inesperados de DynamoDB (WCUs)
- Sin protección contra abuso o ataques DoS

**Solución propuesta:**
- Middleware con `slowapi` (https://github.com/laurentS/slowapi) → rate limit por user_id (ej. 10 requests/minuto)
- O API Gateway con políticas de throttling (requiere migrar de ALB → API Gateway)

---

### 6. Frontend: Polling nunca se detiene si hay error 401

**Ubicación:** `frontend/src/hooks/usePolling.js` y `Dashboard.js`

**Problema:** Si el token JWT expira mientras el polling está activo, el frontend sigue haciendo requests cada 5 segundos (todos fallan con 401), pero no redirige a login.

**Impacto:** Usuario ve dashboard vacío sin indicación clara de por qué no carga.

**Solución propuesta:**
- En `api.js`, interceptar error 401 → limpiar `localStorage` y redirigir a `/login`
- O en `usePolling`, detener polling si recibe error 401

---

### 7. Sin health check en workers (ECS no puede detectar workers muertos)

**Ubicación:** `infra/ecs_workers.tf` — no tiene `healthCheck` en task definition

**Problema:** Si un worker se bloquea (deadlock, error no manejado), ECS no lo detecta porque no hay health check.

**Impacto:** Worker sigue "running" en ECS pero no procesa mensajes (mensajes se quedan en SQS hasta timeout).

**Solución propuesta:**
- Agregar health check con script que verifica que el proceso Python está vivo y respondiendo
- O monitorear métrica custom de "último mensaje procesado" en CloudWatch (si no hay actividad en 10 min → unhealthy)

---

### 8. Contraseñas en texto plano en seeds / tests

**Ubicación:** `backend/seed.py`, `backend/tests/conftest.py`

**Problema:** Contraseñas de usuarios de prueba están hardcoded:
```python
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
```

**Impacto:**
- Riesgo bajo (solo para tests locales), pero si alguien usa el mismo password en producción...
- Seed script crea usuario admin con password conocido públicamente si no se configura env var

**Solución propuesta:**
- En entornos de producción, forzar que `ADMIN_PASSWORD` sea obligatorio (raise exception si no está definido)
- En tests, usar passwords aleatorios generados automáticamente

---

### 9. Sin validación de formato de `date_range`

**Ubicación:** `backend/app/api/schemas/job.py` línea 9

```python
date_range: str = Field(..., description="Date range in format: YYYY-MM-DD to YYYY-MM-DD")
```

**Problema:** El campo tiene descripción pero NO validación real. Un usuario puede enviar `"fecha invalida"` y el backend lo acepta.

**Impacto:** Garbage in, garbage out. Si en el futuro se implementa procesamiento real, fallará.

**Solución propuesta:**
```python
from pydantic import field_validator
import re

@field_validator('date_range')
def validate_date_range(cls, v):
    pattern = r'^\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, v):
        raise ValueError('date_range must match format: YYYY-MM-DD to YYYY-MM-DD')
    return v
```

---

### 10. Sin tests de integración end-to-end

**Ubicación:** `backend/tests/` — solo unit tests con mocks

**Problema:** Los tests actuales mockean DynamoDB y SQS. No hay tests que:
- Levanten LocalStack + backend + worker
- Creen un job real
- Verifiquen que eventualmente se marca como COMPLETED/FAILED

**Impacto:** Regresiones en integración AWS no se detectan hasta deployment.

**Solución propuesta:** Agregar carpeta `tests/integration/` con script que usa `docker-compose` y hace assertions contra el sistema completo.

---

### Resumen de prioridades

| Deuda técnica | Prioridad | Esfuerzo | Impacto si no se resuelve |
|---|---|---|---|
| CORS `allow_origins=["*"]` en producción | 🔴 Alta | Bajo | Vulnerabilidad de seguridad |
| Sin rate limiting en API | 🔴 Alta | Medio | Riesgo de abuso y costos |
| Sin monitoreo de DLQ | 🟡 Media | Medio | Jobs fallidos se pierden silenciosamente |
| Paginación ineficiente (scan completo) | 🟡 Media | Alto | Problemas de performance con >1000 jobs/usuario |
| Worker no lee `WORKER_CONCURRENCY` | 🟡 Media | Bajo | Throughput menor al esperado |
| Sin health check en workers | 🟡 Media | Medio | Workers muertos no se detectan |
| Polling frontend no para en 401 | 🟢 Baja | Bajo | UX confusa al expirar token |
| Logs no estructurados en worker | 🟢 Baja | Medio | Debugging más difícil |
| Sin validación de `date_range` | 🟢 Baja | Bajo | Datos inconsistentes (sin impacto funcional actual) |
| Sin tests de integración E2E | 🟢 Baja | Alto | Regresiones no detectadas temprano |
