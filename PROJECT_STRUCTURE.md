# 📁 Estructura del Proyecto

```
test_prospera/
│
├── 📂 local/                  # 🔧 Entorno de desarrollo con LocalStack
│   ├── docker-compose.yml    # Configuración Docker Compose
│   ├── localstack-init.sh    # Script init LocalStack
│   ├── start_with_sqs.sh     # Helper script
│   ├── .env.example          # Variables de entorno
│   └── README.md             # Documentación del entorno local
│
├── 📂 backend/               # 🐍 API FastAPI
│   ├── app/
│   │   ├── api/              # Endpoints y dependencias
│   │   ├── application/      # Casos de uso
│   │   ├── core/             # Configuración y seguridad
│   │   ├── domain/           # Entidades y enums
│   │   └── infrastructure/   # Repositorios y DB
│   ├── tests/                # Tests unitarios
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── 📂 frontend/              # ⚛️ Aplicación React
│   ├── public/
│   ├── src/
│   │   ├── components/       # Componentes reutilizables
│   │   ├── context/          # Context API (AuthContext)
│   │   ├── hooks/            # Custom hooks (usePolling)
│   │   ├── pages/            # Páginas (Dashboard, LoginPage)
│   │   ├── services/         # API client
│   │   └── styles/           # CSS modules
│   ├── Dockerfile
│   └── package.json
│
├── 📂 worker/                # ⚙️ Worker independiente
│   ├── main.py               # Procesador de cola SQS
│   └── Dockerfile
│
├── 📂 contexto/              # 📝 Documentación del ejercicio
│   ├── contexto_de_ejercicio.md
│   └── diagramas .mermaid
│
├── 📜 dev-start.ps1          # Script para iniciar entorno (Windows)
├── 📜 dev-stop.ps1           # Script para detener entorno (Windows)
├── 📜 dev-logs.ps1           # Script para ver logs (Windows)
├── 📜 dev-start.sh           # Script para iniciar entorno (Linux/Mac)
│
├── 📄 USERS_README.md        # Credenciales de usuarios
├── 📄 README.md              # Este archivo
└── 📄 .gitignore

```

## 🎯 Arquitectura

### Desarrollo Local (LocalStack)
```
┌─────────────┐
│   React     │ :3000
│  (Frontend) │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  FastAPI    │ :8000
│  (Backend)  │
└──────┬──────┘
       │
       ├→ DynamoDB (LocalStack:4566)
       │  ├── Tabla: jobs
       │  └── Tabla: users
       │
       └→ SQS (LocalStack:4566)
          └── Queue: test-queue
             │
             ↓
       ┌──────────┬──────────┐
       │          │          │
   Worker_1   Worker_2   ...
   (WORKER_1) (WORKER_2)
```

### Componentes

| Componente | Tecnología | Puerto | Descripción |
|-----------|------------|--------|-------------|
| **Frontend** | React 18 | 3000 | SPA con formularios y polling |
| **Backend** | FastAPI + Python 3.11 | 8000 | API REST con JWT auth |
| **Workers** | Python 3.11 | - | Procesamiento asíncrono (2 instancias) |
| **Queue** | AWS SQS (LocalStack) | 4566 | Cola de mensajes |
| **Database** | DynamoDB (LocalStack) | 4566 | NoSQL (jobs + users) |

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker & Docker Compose
- Node.js 18+ (solo para desarrollo frontend local)
- Python 3.11+ (solo para desarrollo backend local)

### 1. Clonar e Iniciar

```powershell
# Clonar repositorio
git clone <repo-url>
cd test_prospera

# Iniciar entorno completo
.\dev-start.ps1

# O con docker-compose directamente
cd local
docker-compose up --build
```

### 2. Acceder a la Aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LocalStack**: http://localhost:4566

### 3. Credenciales

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `superadmin` | `superpassword` | admin |
| `user1` | `password123` | user |
| `user2` | `password456` | user |

## 🛠️ Comandos Útiles

```powershell
# Iniciar entorno
.\dev-start.ps1

# Detener entorno
.\dev-stop.ps1

# Ver logs (todos)
.\dev-logs.ps1

# Ver logs de un servicio específico
.\dev-logs.ps1 backend
.\dev-logs.ps1 worker_1

# Reiniciar un servicio
cd local
docker-compose restart backend

# Limpiar todo y empezar de cero
cd local
docker-compose down -v --remove-orphans
docker-compose up --build
```

## 📦 Stack Tecnológico

### Backend
- **FastAPI** - Framework web async
- **Pydantic** - Validación de datos
- **python-jose** - JWT tokens
- **bcrypt** - Password hashing
- **boto3** - AWS SDK (SQS, DynamoDB)

### Frontend
- **React 18** - UI library
- **Bootstrap 5** - CSS framework
- **Context API** - State management
- **Custom Hooks** - usePolling para actualizaciones

### Infraestructura
- **Docker & Docker Compose** - Contenedores
- **LocalStack** - AWS emulator (desarrollo)
- **AWS SQS** - Cola de mensajes
- **AWS DynamoDB** - Base de datos NoSQL

## 🗄️ Esquema de Datos

### Tabla: `jobs`
```
job_id (PK)       : UUID
user_id           : String (GSI)
status            : PENDING | PROCESSING | COMPLETED | FAILED
report_type       : String
date_range        : String
format            : csv | pdf | excel
created_at        : ISO 8601
updated_at        : ISO 8601
result_url        : String (opcional)
```

### Tabla: `users`
```
user_id (PK)      : String
password_hash     : String (bcrypt)
role              : admin | user
created_at        : ISO 8601
```

## 🔐 Seguridad

- ✅ Passwords hasheadas con bcrypt
- ✅ Autenticación JWT
- ✅ Aislamiento de datos por usuario
- ✅ Validación de permisos por rol
- ✅ Variables de entorno para credenciales

## 📚 Documentación Adicional

- [Local Development README](local/README.md) - Entorno de desarrollo
- [Users Documentation](USERS_README.md) - Gestión de usuarios
- [API Documentation](http://localhost:8000/docs) - OpenAPI/Swagger (cuando está corriendo)

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

## 🎨 Características

### Backend
- ✅ Arquitectura limpia (Clean Architecture)
- ✅ Endpoints RESTful (POST, GET, DELETE)
- ✅ Paginación en listados
- ✅ Manejo centralizado de errores
- ✅ Autenticación JWT
- ✅ Validación con Pydantic

### Frontend
- ✅ Formulario de creación de reportes con validación
- ✅ Lista con paginación y actualización automática (polling)
- ✅ Estados visuales con badges de colores
- ✅ Modal de búsqueda por Job ID
- ✅ Diseño responsive (Bootstrap)
- ✅ Manejo de autenticación con Context API

### Workers
- ✅ 2 instancias independientes
- ✅ Procesamiento concurrente
- ✅ Manejo de fallos con VisibilityTimeout
- ✅ Logging identificado por instancia
- ✅ Actualización de estado en tiempo real

## 🔮 Roadmap

- [ ] Pipeline CI/CD con GitHub Actions
- [ ] Despliegue a AWS real (ECS + RDS + SQS real)
- [ ] Tests de integración
- [ ] WebSockets para actualizaciones push
- [ ] Circuit breaker en workers
- [ ] Observabilidad (métricas, traces)

## 👨‍💻 Autor

**Pedro Nel Caro Diaz**

---

📅 Última actualización: Marzo 2026
