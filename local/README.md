# Entorno de Desarrollo Local con LocalStack

Esta carpeta contiene todos los archivos necesarios para ejecutar el proyecto en desarrollo local usando Docker Compose y LocalStack.

## 📁 Contenido

```
local/
├── docker-compose.yml      # Configuración de servicios Docker
├── localstack-init.sh      # Script de inicialización de LocalStack
├── start_with_sqs.sh       # Script legacy para iniciar con SQS
└── .env.example            # Variables de entorno de ejemplo
```

## 🚀 Inicio Rápido

### Desde la raíz del proyecto:

**Windows (PowerShell):**
```powershell
.\dev-start.ps1
```

**Linux/Mac:**
```bash
./dev-start.sh
```

### Desde esta carpeta (local/):

```bash
docker-compose up --build
```

## 🛑 Detener el Entorno

**Desde la raíz:**
```powershell
.\dev-stop.ps1
```

**Desde local/:**
```bash
docker-compose down
```

## 📋 Ver Logs

**Desde la raíz:**
```powershell
# Todos los servicios
.\dev-logs.ps1

# Un servicio específico
.\dev-logs.ps1 backend
.\dev-logs.ps1 frontend
.\dev-logs.ps1 worker_1
```

**Desde local/:**
```bash
docker-compose logs -f backend
```

## 🔧 Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **localstack** | 4566 | Emulador de servicios AWS (SQS, DynamoDB) |
| **backend** | 8000 | API FastAPI |
| **frontend** | 3000 | Aplicación React |
| **worker_1** | - | Worker procesando cola SQS (instancia 1) |
| **worker_2** | - | Worker procesando cola SQS (instancia 2) |
| **sqs-init** | - | Inicialización de cola SQS |
| **users-init** | - | Inicialización de usuarios en DynamoDB |

## 🗄️ Recursos AWS Locales

### SQS
- **Queue Name**: `test-queue`
- **Endpoint**: `http://localhost:4566`

### DynamoDB
- **Tabla jobs**: Almacena trabajos de reportes
  - Partition Key: `job_id`
  - GSI: `UserIdIndex` (sobre `user_id`)
- **Tabla users**: Almacena usuarios del sistema
  - Partition Key: `user_id`
- **Endpoint**: `http://localhost:4566`

## 🔑 Usuarios Pre-creados

Ver archivo `USERS_README.md` en la raíz del proyecto para credenciales.

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LocalStack**: http://localhost:4566

## 🐛 Troubleshooting

### Los contenedores no inician
```bash
cd local
docker-compose down -v
docker-compose up --build
```

### Ver estado de servicios
```bash
cd local
docker-compose ps
```

### Limpiar todo y empezar de cero
```bash
cd local
docker-compose down -v --remove-orphans
docker system prune -f
docker-compose up --build
```

## 📝 Variables de Entorno

Copia `.env.example` a `.env` y ajusta según necesites:

```bash
cp .env.example .env
```

Variables principales:
- `AWS_ACCESS_KEY_ID`: Credencial AWS (usar "test" para local)
- `AWS_SECRET_ACCESS_KEY`: Secret AWS (usar "test" para local)
- `AWS_REGION`: Región AWS (default: us-east-1)
- `SQS_QUEUE_NAME`: Nombre de la cola (default: test-queue)
- `DYNAMODB_TABLE_NAME`: Nombre tabla jobs (default: jobs)
- `USERS_TABLE_NAME`: Nombre tabla users (default: users)

## 🔄 Reiniciar Servicios Específicos

```bash
cd local
docker-compose restart backend
docker-compose restart worker_1 worker_2
docker-compose restart frontend
```

## 📦 Volúmenes Persistentes

- `localstack_data`: Datos de LocalStack (SQS, DynamoDB)

Para limpiar datos persistentes:
```bash
docker-compose down -v
```
