# Backend de Procesamiento Asíncrono de Reportes

## Descripción
Este proyecto implementa un sistema backend para procesamiento asíncrono de reportes, diseñado para plataformas SaaS que requieren manejar trabajos (jobs) de larga duración sin bloquear al usuario. El sistema está construido con **FastAPI**, sigue los principios de **Clean Architecture** y está preparado para evolucionar hacia una solución escalable en AWS (SQS, ECS, RDS).

## Arquitectura
El backend está organizado en capas bien definidas para garantizar bajo acoplamiento, alta mantenibilidad y facilidad de pruebas:

- **domain/**: Entidades y enums puros, sin dependencias externas. Aquí se define la lógica de negocio central (ej: entidad `Job`, enum `JobStatus`).
- **application/**: Casos de uso (use cases) y puertos (interfaces). Orquesta la lógica de negocio y define contratos para la infraestructura.
- **infrastructure/**: Implementaciones concretas de los puertos, como el repositorio SQLAlchemy y la configuración de la base de datos (SQLite en esta fase).
- **api/**: Esquemas Pydantic, rutas FastAPI y manejadores de errores. Los endpoints solo interactúan con los casos de uso, nunca con la infraestructura directamente.
- **worker/**: Implementación temporal de un worker asíncrono usando threading, simula el procesamiento de jobs.

## Flujo del Sistema
1. El usuario solicita un nuevo reporte vía `POST /jobs`.
2. El sistema crea el job en estado `PENDING` y responde inmediatamente.
3. Un fake worker se lanza automáticamente en un thread separado, cambia el estado a `PROCESSING`, simula el trabajo y finalmente marca el job como `COMPLETED` (o `FAILED` si ocurre un error).
4. El frontend (o cliente) consulta el estado del job periódicamente (`GET /jobs/{job_id}`) hasta que se completa.

Este flujo desacopla la experiencia del usuario del procesamiento real, permitiendo escalar y manejar múltiples trabajos concurrentes.

## Ejecución Local

1. **Clona el repositorio y navega al directorio backend:**
   ```bash
   git clone <repo_url>
   cd backend
   ```
2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Inicializa la base de datos:**
   ```bash
   python app/infrastructure/db/init_db.py
   ```
4. **Ejecuta el servidor FastAPI:**
   ```bash
   uvicorn main:app --reload
   ```

## Endpoints Disponibles



### Autenticación JWT y Roles

#### Obtener un token
- **POST /auth/login**
- Body:
  ```json
  {
    "user_id": "superadmin",
    "password": "superpassword"
  }
  ```
- Para otros usuarios, puedes usar cualquier password.
- Respuesta:
  ```json
  {
    "access_token": "<jwt_token>",
    "token_type": "bearer"
  }
  ```

El token generado tendrá el payload:
```json
{
  "sub": "superadmin",
  "role": "admin",
  "exp": ...
}
```

Para cualquier otro usuario:
```json
{
  "sub": "usuario123",
  "role": "user",
  "exp": ...
}
```

#### Usar el token en endpoints protegidos
Todos los endpoints requieren el header:
```
Authorization: Bearer <jwt_token>
```

#### Acceso por rol
- El endpoint **GET /jobs** está protegido y solo accesible para usuarios con rol "admin" (por ejemplo, superadmin).
- Si se usa un token con rol "user", se retorna HTTP 403 Forbidden.

### Crear un nuevo job
- **POST /jobs**
- Headers: `Authorization: Bearer <jwt_token>`
- Body:
  ```json
  {
    "report_type": "ventas"
  }
  ```
- Respuesta:
  ```json
  {
    "job_id": "<uuid>",
    "user_id": "usuario123",
    "status": "PENDING",
    "report_type": "ventas",
    "created_at": "2026-03-18T12:00:00Z",
    "updated_at": "2026-03-18T12:00:00Z",
    "result_url": null
  }
  ```

### Consultar un job por ID
- **GET /jobs/{job_id}**
- Headers: `Authorization: Bearer <jwt_token>`
- Respuesta:
  ```json
  {
    "job_id": "<uuid>",
    "user_id": "usuario123",
    "status": "PROCESSING",
    "report_type": "ventas",
    "created_at": "2026-03-18T12:00:00Z",
    "updated_at": "2026-03-18T12:00:10Z",
    "result_url": "https://dummy.result/<uuid>"
  }
  ```

### Listar jobs del usuario (paginado)
- **GET /jobs?limit=10&offset=0**
- Headers: `Authorization: Bearer <jwt_token>`
- Respuesta:
  ```json
  {
    "jobs": [
      { ... },
      { ... }
    ]
  }
  ```

## Decisiones Técnicas

- **Clean Architecture:**
  - Permite desacoplar la lógica de negocio de frameworks y detalles de infraestructura.
  - Facilita la evolución futura (por ejemplo, cambiar SQLite por PostgreSQL o SQS sin modificar la lógica de negocio).
  - Mejora la testabilidad y mantenibilidad del código.

- **Fake Worker:**
  - Simula procesamiento asíncrono real usando threads.
  - Permite probar el flujo completo sin depender de AWS ni servicios externos.
  - El diseño está preparado para reemplazar fácilmente el fake worker por un consumidor real de SQS en el futuro.

## Próximos Pasos
- Integrar AWS SQS como sistema de colas para desacoplar el procesamiento real.
- Migrar la base de datos a PostgreSQL o RDS.
- Desplegar el backend en AWS ECS o Fargate.
- Implementar autenticación JWT real.
- Mejorar la observabilidad y manejo de errores avanzados.

---

¿Dudas o sugerencias? Abre un issue o contacta al responsable del repositorio.
