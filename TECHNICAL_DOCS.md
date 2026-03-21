# TECHNICAL_DOCS.md — Sistema de Procesamiento Asíncrono de Reportes

> Generado con GitHub Copilot a partir del código del proyecto. Revisado y ajustado manualmente.

---

## 1. Resumen del sistema

El sistema permite a usuarios autenticados solicitar **reportes de datos bajo demanda**. Como el procesamiento puede tardar entre 5 y 30 segundos, el flujo es completamente asíncrono:

1. El usuario envía un formulario desde React → FastAPI crea el job en DynamoDB y publica un mensaje en SQS.
2. Los workers (en contenedores ECS separados) consumen la cola y actualizan el estado del job.
3. React hace polling cada 5 segundos y muestra el estado en tiempo real con badges de color.

---

## 2. Diagrama de arquitectura

La arquitectura del sistema sigue un patrón **event-driven** con componentes desacoplados. El frontend se comunica con el backend a través de un ALB, el backend publica eventos en SQS, y los workers procesan estos eventos de forma independiente.

**Características clave:**
- **Separación de responsabilidades:** Frontend (UI), Backend (API), Workers (procesamiento)
- **Escalabilidad horizontal:** Cada componente puede escalar independientemente
- **Resiliencia:** Fallo en un worker no afecta al backend ni al frontend
- **Observabilidad:** Todos los servicios envían logs a CloudWatch

```mermaid
graph TD
    User["🧑 Usuario (browser)"]
    CF["CloudFront CDN"]
    S3["S3 (React build)"]
    ALB["Application Load Balancer"]
    Backend["ECS Fargate — Backend (FastAPI)"]
    Worker1["ECS Fargate — Worker #1"]
    Worker2["ECS Fargate — Worker #2"]
    SQS["SQS — jobs-queue"]
    DLQ["SQS — jobs-dlq (Dead Letter)"]
    DDB_Jobs["DynamoDB — prosperas-jobs"]
    DDB_Users["DynamoDB — prosperas-users"]
    SSM["SSM Parameter Store (JWT_SECRET)"]
    ECR["ECR (imágenes Docker)"]
    GH["GitHub Actions (CI/CD)"]

    User -->|HTTPS| CF
    CF -->|SPA / archivos| S3
    User -->|API calls| ALB
    ALB -->|:8000| Backend
    Backend -->|"PUT/GET jobs"| DDB_Jobs
    Backend -->|"GET users"| DDB_Users
    Backend -->|"SendMessage"| SQS
    Backend -->|"GetSecretValue"| SSM
    Worker1 -->|"ReceiveMessage"| SQS
    Worker2 -->|"ReceiveMessage"| SQS
    Worker1 -->|"UpdateItem"| DDB_Jobs
    Worker2 -->|"UpdateItem"| DDB_Jobs
    SQS -->|"maxReceive=3"| DLQ
    GH -->|"docker push"| ECR
    GH -->|"ecs update-service"| Backend
    GH -->|"s3 sync"| S3
    ECR -.->|"pullImage"| Backend
    ECR -.->|"pullImage"| Worker1
```

---

## 3. Servicios AWS utilizados

La elección de servicios AWS se basó en los principios de **serverless-first**, **pago por uso** y **gestión mínima de infraestructura**. Todos los servicios son gestionados por AWS, lo que reduce significativamente la carga operativa.

**Criterios de selección:**
- **Sin gestión de servidores:** DynamoDB, SQS, S3, CloudFront, ECS Fargate (sin EC2)
- **Auto-scaling nativo:** Los servicios escalan automáticamente según demanda
- **Integración nativa:** Servicios AWS se comunican sin configuración compleja
- **Costo optimizado:** Solo pagas por lo que usas (sin infraestructura ociosa)

| Servicio | Rol en el sistema | Por qué se eligió |
|---|---|---|
| **SQS** | Cola de mensajes entre API y workers | Servicio gestionado, precio por mensaje, DLQ nativa, reintentos automáticos. Kafka sería sobre-ingeniería para este volumen. |
| **DynamoDB** | Persistencia de jobs y usuarios | Sin servidor, pago por uso, latencia sub-milisegundo en lecturas por PK. El GSI `UserIdIndex` permite listar jobs por usuario eficientemente. RDS requeriría una VPC más elaborada y coste fijo. |
| **ECS Fargate** | Hosting de backend y workers | Sin gestión de EC2, auto-scaling por tarea, aislamiento real entre backend y workers. EC2 era opción pero Fargate es más adecuado para cargas variables. |
| **ALB** | Entrada HTTP al backend | Health checks automáticos, terminación SSL (cuando se añada ACM). Target group tipo IP para Fargate. |
| **ECR** | Registro de imágenes Docker | Integración nativa con ECS sin credenciales extras. Lifecycle policy para limpiar imágenes antiguas. |
| **S3** | Hosting del frontend (archivos estáticos) | Sin servidor, coste casi cero para archivos < 1 GB, integración nativa con CloudFront. |
| **CloudFront** | CDN del frontend | Caché global, HTTPS automático con certificado AWS, SPA routing (404 → index.html). |
| **SSM Parameter Store** | Secreto JWT | SecureString cifrado con KMS. Evita guardar secretos en variables de entorno del contenedor en texto plano. |

---

## 4. Modelo de datos

El modelo de datos está diseñado para DynamoDB, una base de datos NoSQL que requiere planificar los patrones de acceso por adelantado. Las tablas están desnormalizadas para optimizar las consultas más frecuentes.

**Patrones de acceso soportados:**
1. Obtener job por ID (GetItem por PK)
2. Listar jobs de un usuario ordenados por fecha (Query en GSI UserIdIndex)
3. Autenticación de usuario (GetItem por user_id)

**Decisión clave:** Se usa un **Global Secondary Index (GSI)** en la tabla de jobs para permitir consultas eficientes por `user_id` sin hacer Scan completo de la tabla.

### Tabla `prosperas-jobs`

| Atributo | Tipo | Descripción |
|---|---|---|
| `job_id` | String (UUID) | PK — identificador único del job |
| `user_id` | String | Usuario que creó el job (GSI: UserIdIndex) |
| `status` | String | `PENDING` / `PROCESSING` / `COMPLETED` / `FAILED` |
| `report_type` | String | Tipo de reporte solicitado |
| `date_range` | String | Rango de fechas (opcional) |
| `format` | String | Formato salida (PDF, CSV, etc.) |
| `created_at` | String (ISO8601) | Timestamp de creación |
| `updated_at` | String (ISO8601) | Última actualización de estado |
| `result_url` | String | URL del resultado (sólo en COMPLETED) |
| `error_msg` | String | Mensaje de error (sólo en FAILED) |

**GSI:** `UserIdIndex` — PK: `user_id`, SK: `created_at` — permite listar jobs de un usuario sin scan.

### Tabla `prosperas-users`

| Atributo | Tipo | Descripción |
|---|---|---|
| `user_id` | String | PK — nombre de usuario |
| `password_hash` | String | bcrypt hash |
| `role` | String | `user` (extensible a `admin`) |

---

## 5. Flujo completo de un job

Este diagrama de secuencia muestra el ciclo de vida completo de un job desde que el usuario lo solicita hasta que ve el resultado final. El flujo está dividido en **tres fases** claramente diferenciadas:

1. **Fase 1: Crear Job** — El usuario envía la solicitud, el backend crea el registro y encola el mensaje
2. **Fase 2: Procesamiento Asíncrono** — Un worker consume el mensaje, procesa el job y actualiza su estado
3. **Fase 3: Polling desde Frontend** — El frontend consulta periódicamente el estado hasta que el job termina

**Nota importante:** El frontend recibe una respuesta inmediata (201 Created) sin esperar a que el job termine de procesarse. Esto es clave para la experiencia de usuario en operaciones que pueden tardar varios segundos.

```mermaid
sequenceDiagram
    participant User as 🧑 Usuario
    participant Frontend as React App
    participant ALB as ALB
    participant Backend as FastAPI Backend
    participant DDB as DynamoDB
    participant SQS as SQS Queue
    participant Worker as Worker (ECS)
    participant DLQ as Dead Letter Queue

    Note over User,DLQ: Fase 1: Crear Job
    User->>Frontend: Llena formulario de reporte
    Frontend->>ALB: POST /jobs {report_type, date_range, format}
    ALB->>Backend: Forward request
    Backend->>DDB: PutItem job {status: PENDING}
    DDB-->>Backend: OK
    Backend->>SQS: SendMessage {job_id}
    SQS-->>Backend: MessageId
    Backend-->>ALB: 201 Created {job_id, status: PENDING}
    ALB-->>Frontend: Response
    Frontend-->>User: "Job creado, ID: xxx"

    Note over User,DLQ: Fase 2: Procesamiento Asíncrono
    Worker->>SQS: ReceiveMessage (long-polling 10s)
    SQS-->>Worker: {job_id}
    Note over Worker: Visibility timeout 120s
    Worker->>DDB: UpdateItem job {status: PROCESSING}
    DDB-->>Worker: OK
    Worker->>Worker: sleep(random 5-30s)<br/>[simula procesamiento]
    
    alt Procesamiento exitoso (50%)
        Worker->>DDB: UpdateItem {status: COMPLETED, result_url}
        DDB-->>Worker: OK
        Worker->>SQS: DeleteMessage
    else Procesamiento fallido (50%)
        Worker->>DDB: UpdateItem {status: FAILED, error_msg}
        DDB-->>Worker: OK
        Worker->>SQS: DeleteMessage
    end

    Note over User,DLQ: Fase 3: Polling desde Frontend
    loop Cada 5 segundos
        Frontend->>ALB: GET /jobs/{job_id}
        ALB->>Backend: Forward
        Backend->>DDB: GetItem job_id
        DDB-->>Backend: {job_id, status, ...}
        Backend-->>ALB: 200 OK job data
        ALB-->>Frontend: Response
        Frontend-->>User: Actualiza badge de estado
    end

    Note over SQS,DLQ: Manejo de Fallos
    alt Worker falla 3 veces
        SQS->>DLQ: Mover mensaje (maxReceiveCount=3)
        Note over DLQ: Retención 14 días<br/>Requiere redrive manual
    end
```

---

## 6. Decisiones de diseño y trade-offs

Todo sistema software implica **trade-offs** — elegir una solución significa renunciar a los beneficios de otra. Esta sección documenta las decisiones técnicas más importantes y las alternativas que se consideraron pero se descartaron.

**Filosofía de diseño:**
- **Simplicidad sobre sofisticación:** Elegir la solución más simple que resuelva el problema
- **Iterar, no sobre-diseñar:** Implementar lo necesario ahora, dejar extensiones para después
- **Costo-eficiencia:** Evitar servicios caros cuando hay alternativas más baratas que funcionan
- **Despliegue rápido:** Priorizar soluciones que permitan llegar a producción en días, no semanas

Cada decisión está justificada con las razones técnicas y de negocio que la motivaron.

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| DynamoDB en lugar de RDS | PostgreSQL (RDS) | Sin VPC compleja, sin coste fijo, pago por lectura/escritura. Para un CRUD de jobs es suficiente. |
| Polling en frontend (5s) | WebSockets / SSE | Más simple y robusto. Evita gestión de conexiones persistentes en Fargate. WebSockets se puede añadir como mejora posterior. |
| ECS Fargate desired_count=2 para workers | 1 worker o Lambda | 2 workers garantizan procesamiento paralelo (requisito). Lambda tendría cold starts y límite de 15 min. |
| SQS visibility_timeout=120s | Valor por defecto (30s) | El job puede tardar hasta 30s + overhead → 120s evita que otro worker reintente un job ya en proceso. |
| JWT en SSM SecureString | Variable de entorno | Los env vars de ECS se pueden leer en AWS Console. SSM cifra con KMS y audita el acceso. |
| Terraform para IaC | CDK / SAM / CloudFormation | Terraform tiene soporte maduro para todos los recursos usados, plan/apply es más predecible. |

---

## 7. Setup local (LocalStack)

### Prerequisitos

- Docker Desktop instalado y corriendo
- `docker compose` v2

**Nota:** No necesitas instalar LocalStack por separado. Viene como servicio en el `docker-compose.yml` (imagen `localstack/localstack:3.0`) y se levanta automáticamente junto con backend, workers y frontend.

### Pasos

```bash
# 0. Verificar que Docker Desktop está corriendo
docker --version
# Debe mostrar: Docker version 20.x o superior
# Si da error, abre Docker Desktop y espera a que arranque completamente

docker compose version
# Debe mostrar: Docker Compose version v2.x o superior

# 1. Clonar el repo
git clone https://github.com/carmagedon07/test_Prosperas.git
cd test_Prosperas

# 2. Copiar variables de entorno
cp .env.example .env
# NOTA: Para desarrollo local NO es necesario editar .env
# Los valores por defecto ya están configurados para LocalStack
# Solo edita si necesitas cambiar puertos o credenciales de prueba

# 3. Ir a la carpeta local/ y levantar todos los servicios
cd local
docker compose up --build

# La primera vez tarda ~2 minutos mientras construye las imágenes y
# LocalStack inicializa los recursos (SQS + DynamoDB).
# ⚠️ ESPERA a ver estos mensajes en los logs antes de continuar:
#    ✓ "localstack   | Ready." 
#    ✓ "aws-init    | ✅ Queue created: jobs-queue"
#    ✓ "aws-init    | ✅ Table created: jobs"
#    ✓ "backend     | INFO:     Application startup complete."

# 4. Verificar que LocalStack está listo (en otra terminal)
curl http://localhost:4566/_localstack/health
# Debe responder con JSON mostrando servicios "available"

# Si LocalStack NO responde:
#   - Espera 30 segundos más (puede tardar en arrancar)
#   - Verifica logs: docker compose logs localstack
#   - Reinicia: docker compose down -v && docker compose up --build

# 5. Acceder a la app (desde otra terminal, dejar docker compose corriendo)
#   Frontend:  http://localhost:3000
#   Backend:   http://localhost:8000
#   API Docs:  http://localhost:8000/docs
#   LocalStack: http://localhost:4566

# 6. Crear un usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser", "password": "pass1234"}'

# 7. Hacer login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser", "password": "pass1234"}'
# → guarda el token recibido

# 8. Crear un job
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"report_type": "sales", "date_range": "2024-01", "format": "PDF"}'
```

### Servicios del docker-compose

| Servicio | Puerto | Descripción |
|---|---|---|
| `localstack` | 4566 | Emula SQS + DynamoDB |
| `init-aws` | — | Script que crea la tabla DynamoDB y cola SQS al arrancar |
| `backend` | 8000 | FastAPI |
| `worker` | — | SQS Worker (instancia 1) |
| `worker2` | — | SQS Worker (instancia 2) |
| `frontend` | 3000 | React |

### Solución de problemas comunes

| Problema | Causa | Solución |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop no está corriendo | Abre Docker Desktop y espera a que muestre "Engine running" |
| `connection refused localhost:4566` | LocalStack aún no arrancó | Espera ~30 segundos más. Verifica logs: `docker compose logs localstack` |
| `ResourceNotFoundException: jobs table` | Las tablas DynamoDB no se crearon | Verifica logs del servicio `aws-init`: `docker compose logs aws-init`. Si falló, reinicia: `docker compose down -v && docker compose up --build` |
| Backend no arranca (port 8000 ocupado) | Puerto 8000 ya en uso por otro proceso | Mata el proceso: `lsof -ti:8000 \| xargs kill` (Mac/Linux) o cambia `BACKEND_PORT` en `.env` |
| Frontend no carga en localhost:3000 | Puerto 3000 ocupado o contenedor falló | Verifica logs: `docker compose logs frontend`. Cambia puerto: `ports: "3001:3000"` en docker-compose.yml |
| Workers no procesan mensajes | SQS_ENDPOINT apunta a localhost en vez de localstack | Verifica que `.env` tiene `SQS_ENDPOINT=http://localstack:4566` (nombre del servicio, no localhost) |
| `docker compose: command not found` | Docker Compose v1 instalado (deprecated) | Instala v2: https://docs.docker.com/compose/install/ o usa `docker-compose` (con guión) |

---

## 8. Despliegue a producción

### Prerequisitos

Antes de desplegar a AWS, asegúrate de tener instalado:

- **Terraform** v1.0 o superior
- **AWS CLI** v2 configurado con credenciales de administrador
- Cuenta AWS con permisos para crear recursos (VPC, ECS, DynamoDB, SQS, ALB, etc.)

#### Verificar instalación de Terraform

```bash
terraform --version
# Debe mostrar: Terraform v1.x.x o superior
```

**Si NO está instalado:**

- **Windows (con Chocolatey):**
  ```bash
  choco install terraform
  ```

- **macOS (con Homebrew):**
  ```bash
  brew install terraform
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
  sudo apt update && sudo apt install terraform
  ```

- **Manual (cualquier OS):**  
  Descarga desde https://www.terraform.io/downloads y agrega al PATH

#### Verificar instalación de AWS CLI

```bash
aws --version
# Debe mostrar: aws-cli/2.x.x o superior

# Configurar credenciales (si no lo has hecho)
aws configure
# Ingresa: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)
```

**Si NO está instalado:**  
Sigue la guía oficial: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### Infraestructura (Terraform — carpeta `infra/`)

```bash
# 0. Verificar que Terraform y AWS CLI están configurados
terraform --version
aws sts get-caller-identity
# Debe mostrar tu UserId, Account y Arn (confirma que las credenciales funcionan)

# 1. Ir a la carpeta de infraestructura
cd infra
cp terraform.tfvars.example terraform.tfvars

# 2. Editar terraform.tfvars con tus valores
# OBLIGATORIO: jwt_secret (genera uno seguro con: openssl rand -base64 32)
# OPCIONAL: image_tag, environment, backend_cpu, etc.

# 3. Inicializar Terraform (descarga providers de AWS)
terraform init

# 4. Ver qué recursos se crearán (IMPORTANTE: revisar antes de aplicar)
terraform plan
# Deberías ver ~44 recursos: VPC, subnets, SQS, DynamoDB, ECS, ALB, CloudFront, etc.

# 5. Crear todos los recursos en AWS (~3-5 min)
terraform apply
# Escribe 'yes' cuando pregunte

# ⚠️ NOTA: La primera vez puede fallar el health check de ECS porque
# las imágenes Docker aún no existen en ECR. Si eso pasa:
#   1. Copia los outputs de ECR (ecr_backend_url, ecr_worker_url)
#   2. Haz push manual de las imágenes (ver sección siguiente)
#   3. Re-ejecuta: terraform apply

# 6. Al finalizar, anota los outputs:
terraform output backend_url            # URL del ALB (API)
terraform output cloudfront_url         # URL del frontend
terraform output ecr_backend_url        # Para primer push manual
terraform output ecr_worker_url         # Para primer push manual
terraform output -json cicd_secret_access_key  # Para GitHub Secrets (guarda seguro)
```

### GitHub Secrets requeridos

Después de `terraform apply`, necesitas configurar estos secrets en tu repositorio GitHub para que el CI/CD funcione.

#### Cómo agregar GitHub Secrets (paso a paso)

1. **Ve a tu repositorio en GitHub**  
   https://github.com/TU_USUARIO/test_Prosperas

2. **Navega a Settings → Secrets and variables → Actions**  
   O directo: `https://github.com/TU_USUARIO/test_Prosperas/settings/secrets/actions`

3. **Click en "New repository secret"** para cada uno de los siguientes:

#### Secrets a configurar

| Secret | Obtener valor | Ejemplo |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | `terraform output cicd_access_key_id` | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | `terraform output -json cicd_secret_access_key` (quita las comillas) | `wJalrXUt...` |
| `ECR_BACKEND_REPO` | `terraform output ecr_backend_url` | `521434189536.dkr.ecr.us-east-1.amazonaws.com/prosperas-backend` |
| `ECR_WORKER_REPO` | `terraform output ecr_worker_url` | `521434189536.dkr.ecr.us-east-1.amazonaws.com/prosperas-worker` |
| `REACT_APP_API_URL` | `terraform output backend_url` (agregar `http://` al inicio) | `http://prosperas-alb-1234567890.us-east-1.elb.amazonaws.com` |
| `S3_BUCKET` | `terraform output s3_frontend_bucket` | `prosperas-frontend-abcd1234` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `terraform output cloudfront_distribution_id` | `E1A2B3C4D5E6F7` |

#### Script para obtener todos los valores

```bash
# Corre esto desde la carpeta infra/ para copiar y pegar fácilmente:
echo "AWS_ACCESS_KEY_ID=$(terraform output -raw cicd_access_key_id)"
echo "AWS_SECRET_ACCESS_KEY=$(terraform output -raw cicd_secret_access_key)"
echo "ECR_BACKEND_REPO=$(terraform output -raw ecr_backend_url)"
echo "ECR_WORKER_REPO=$(terraform output -raw ecr_worker_url)"
echo "REACT_APP_API_URL=http://$(terraform output -raw backend_url)"
echo "S3_BUCKET=$(terraform output -raw s3_frontend_bucket)"
echo "CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)"
```

#### Verificar que los secrets están configurados

1. En GitHub: Settings → Secrets and variables → Actions
2. Deberías ver 7 secrets listados (los valores están ocultos, solo se muestran los nombres)
3. Si falta alguno, el pipeline fallará con error: `Error: Secret AWS_ACCESS_KEY_ID not found`

#### Primer push manual (solo primera vez)

Si el pipeline falla porque las imágenes no existen en ECR, haz este push manual:

```bash
# Desde la raíz del proyecto:

# 1. Login a ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw ecr_backend_url | cut -d'/' -f1)

# 2. Build y push backend
cd backend
docker build -t $(cd ../infra && terraform output -raw ecr_backend_url):latest .
docker push $(cd ../infra && terraform output -raw ecr_backend_url):latest

# 3. Build y push worker
cd ../worker
docker build -t $(cd ../infra && terraform output -raw ecr_worker_url):latest .
docker push $(cd ../infra && terraform output -raw ecr_worker_url):latest

# 4. Forzar nuevo deployment en ECS
aws ecs update-service --cluster prosperas-cluster --service prosperas-backend --force-new-deployment
aws ecs update-service --cluster prosperas-cluster --service prosperas-worker --force-new-deployment
```

Luego, cada push a `main` disparará el pipeline automáticamente.

### Pipeline CI/CD (GitHub Actions — `.github/workflows/deploy.yml`)

El proyecto utiliza **GitHub Actions** para automatizar completamente el despliegue a producción. Esto elimina errores humanos, garantiza consistencia en cada deployment y permite iterar rápidamente.

#### ¿Cómo funciona?

Cada vez que haces `git push origin main`, GitHub Actions detecta el cambio y ejecuta el pipeline definido en `.github/workflows/deploy.yml`. El workflow completo tarda ~5-8 minutos y no requiere intervención manual.

#### Ventajas del pipeline automatizado

- **Zero-downtime deployment:** ECS actualiza las tasks gradualmente (rolling update)
- **Rollback automático:** Si el health check falla, ECS revierte a la versión anterior
- **Builds paralelos:** Backend, worker y frontend se construyen simultáneamente
- **Caché optimizado:** Docker layers y dependencias npm se cachean entre builds
- **Seguridad:** Las credenciales AWS están en GitHub Secrets, no en el código

#### Flujo visual del pipeline

Cada push a la rama `main` dispara el siguiente flujo automatizado:

```mermaid
graph LR
    A[🔍 Detect Changes<br/>Detecta qué cambió<br/>backend/frontend/worker] --> B[🧪 Run Tests<br/>pytest backend]
    
    B --> C1[🏗️ Build Backend<br/>docker build<br/>backend:latest]
    B --> C2[🏗️ Build Frontend<br/>npm run build<br/>optimized bundle]
    B --> C3[🏗️ Build Worker<br/>docker build<br/>worker:latest]
    
    C1 --> D1[📦 Push to ECR<br/>backend image]
    C3 --> D3[📦 Push to ECR<br/>worker image]
    
    D1 --> E1[🚀 Deploy Backend<br/>ECS update-service<br/>prosperas-backend]
    D3 --> E3[🚀 Deploy Worker<br/>ECS update-service<br/>prosperas-worker]
    C2 --> E2[🚀 Deploy Frontend<br/>S3 sync + CloudFront<br/>invalidation]
    
    E1 --> F[✅ Health Check<br/>ALB /health endpoint<br/>Wait for stable]
    E3 --> F
    E2 --> F
    
    F --> G[✨ Deployment Complete]
    
    style A fill:#2d5f8d
    style B fill:#5d9c59
    style C1 fill:#8b4513
    style C2 fill:#8b4513
    style C3 fill:#8b4513
    style D1 fill:#ff8c42
    style D3 fill:#ff8c42
    style E1 fill:#8b5cf6
    style E2 fill:#8b5cf6
    style E3 fill:#8b5cf6
    style F fill:#10b981
    style G fill:#059669
```

**Etapas del pipeline:**

1. **Detect Changes** — Analiza qué archivos cambiaron (backend/, frontend/, worker/, infra/)
2. **Run Tests** — Ejecuta pytest del backend antes de construir
3. **Build** — Construye imágenes Docker (backend, worker) y bundle de React (frontend) en paralelo
4. **Push to ECR** — Sube las imágenes Docker al registro ECR de AWS
5. **Deploy** — Actualiza servicios ECS (backend, worker) y sube archivos a S3/CloudFront (frontend) en paralelo
6. **Health Check** — Verifica que el ALB responde 200 en `/health` antes de finalizar
7. **Complete** — Deployment exitoso, aplicación actualizada en producción

---

## 9. Variables de entorno

Las variables de entorno permiten configurar el comportamiento de la aplicación sin modificar el código. Este proyecto utiliza un diseño **dual-mode** que funciona tanto en **desarrollo local con LocalStack** como en **producción con AWS real**.

### Diferencias clave entre entornos

- **Desarrollo local:** Los endpoints apuntan a LocalStack (`http://localstack:4566`), credenciales dummy (`test`/`test`), nombres cortos de recursos (`jobs`, `users`, `jobs-queue`)
  
- **Producción AWS:** Sin endpoints override (boto3 usa AWS real), credenciales IAM (sin `AWS_ACCESS_KEY_ID` en env vars, se usa IAM Role de ECS), nombres con prefijo (`prosperas-jobs`, `prosperas-users`)

### Archivo de configuración

- **Local:** `.env` (copiado de `.env.example`, no está en git)
- **Producción:** Variables inyectadas directamente en ECS Task Definition (ver `infra/ecs_backend.tf` y `infra/ecs_workers.tf`)

**Regla importante:** Si una variable termina en `_ENDPOINT` y está **vacía o ausente**, boto3 automáticamente usa AWS real. Si está **definida**, usa el endpoint especificado (LocalStack).

### Tabla completa de variables

| Variable | Descripción | Valor local | Valor producción |
|---|---|---|---|
| `AWS_REGION` | Región AWS | `us-east-1` | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Credencial AWS | `test` (localstack) | IAM CI/CD user key |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS | `test` (localstack) | IAM CI/CD user secret |
| `DYNAMODB_ENDPOINT` | Override endpoint DynamoDB | `http://localstack:4566` | *(vacío → AWS real)* |
| `SQS_ENDPOINT` | Override endpoint SQS | `http://localstack:4566` | *(vacío → AWS real)* |
| `JOBS_TABLE_NAME` | Tabla DynamoDB de jobs | `jobs` | `prosperas-jobs` |
| `USERS_TABLE_NAME` | Tabla DynamoDB de usuarios | `users` | `prosperas-users` |
| `SQS_QUEUE_NAME` | Nombre de la cola SQS | `jobs-queue` | `prosperas-jobs-queue` |
| `SQS_QUEUE_URL` | URL completa de SQS (opcional) | Construida dinámicamente | Construida con `get_queue_url` |
| `JWT_SECRET` | Secreto para firmar JWT | `secret_local` | Leído de SSM en ECS |
| `JWT_EXPIRY_MINUTES` | Vida útil del token (minutos) | `60` | `60` |
| `REACT_APP_API_URL` | URL base del backend | `http://localhost:8000` | URL del ALB |

---

## 10. Tests

El proyecto incluye una suite de **tests unitarios** que validan la lógica de negocio de los casos de uso. Los tests están escritos con **pytest** y cubren ~65% del código del backend.

**Características de los tests:**
- **Tests unitarios puros:** Usan mocks en memoria, no requieren AWS ni LocalStack
- **Rápidos:** Se ejecutan en ~2 segundos
- **Ejecutados en CI/CD:** Cada push a main ejecuta los tests antes de desplegar
- **Cobertura medible:** Se puede generar reporte de cobertura con `pytest --cov`

**Filosofía de testing:**
- Se testean **casos de uso** (capa de aplicación), no infraestructura (repositorios)
- Los repositorios se mockean con implementaciones in-memory
- Se validan transiciones de estado, validaciones, y casos borde

**Cobertura actual:** 65% (23 tests pasando). Para alcanzar 70% se necesitarían ~7 tests adicionales de API endpoints y repositorios con boto3 mocks.

```bash
# Desde la raíz del proyecto
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v

# Suites disponibles:
# tests/application/use_cases/test_create_job.py       → crea job con mock repository
# tests/application/use_cases/test_get_job.py          → obtiene job existente / 404
# tests/application/use_cases/test_job_use_cases.py    → casos borde (jobs vacíos, paginación)
# tests/application/use_cases/test_update_job_status.py → transiciones de estado
```

Los tests usan repositorios mock en memoria — no requieren DynamoDB ni LocalStack.
