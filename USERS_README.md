# Usuarios del Sistema

## Tabla de Usuarios en DynamoDB

Los usuarios ahora se almacenan en DynamoDB con contraseñas hasheadas usando bcrypt.

### Usuarios Disponibles

| User ID | Contraseña | Rol | Permisos |
|---------|------------|-----|----------|
| `superadmin` | `superpassword` | admin | Puede eliminar todos los jobs |
| `user1` | `password123` | user | Puede ver y crear sus propios jobs |
| `user2` | `password456` | user | Puede ver y crear sus propios jobs |

## Estructura de la Tabla `users`

```
Tabla: users
Partition Key: user_id (String)

Campos:
- user_id: String (PK)
- password_hash: String (bcrypt hash)
- role: String ("admin" | "user")
- created_at: String (ISO 8601 timestamp)
```

## Cambios Implementados

### 1. Backend
- ✅ Agregado `bcrypt` a requirements.txt
- ✅ Nuevo repositorio: `UserRepositoryDynamoDB`
- ✅ Endpoint `/auth/login` ahora autentica contra DynamoDB
- ✅ Contraseñas hasheadas de forma segura con bcrypt

### 2. Infraestructura
- ✅ Tabla `users` creada automáticamente en LocalStack
- ✅ Nuevo servicio `users-init` en docker-compose.yml
- ✅ Script `init_users.py` para poblar usuarios iniciales

### 3. Permisos
- ✅ Endpoint `GET /jobs` accesible para todos los usuarios
- ✅ Cada usuario ve solo sus propios jobs (filtrado por user_id)
- ✅ Endpoint `DELETE /jobs` mantiene restricción de admin

## Pruebas

### Login con user1
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
 -d '{"user_id": "user1", "password": "password123"}'
```

### Login con user2
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user2", "password": "password456"}'
```

### Login con superadmin
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "superadmin", "password": "superpassword"}'
```

## Comportamiento del Sistema

1. **Aislamiento de datos**: Cada usuario solo puede ver sus propios jobs
2. **Autenticación segura**: Contraseñas nunca se almacenan en texto plano
3. **Verificación**: bcrypt compara el hash al hacer login
4. **Roles**: El token JWT incluye el rol del usuario para autorización

## Verificar Usuarios en DynamoDB

```bash
# Ver todos los usuarios
docker exec prospera_localstack awslocal dynamodb scan \
  --table-name users --endpoint-url http://localhost:4566
```

## Notas de Seguridad

- ⚠️ En **producción**, usar una solución de gestión de usuarios más robusta (AWS Cognito, Auth0, etc.)
- ⚠️ La clave `SECRET_KEY` en `security.py` debe ser una variable de entorno
- ⚠️ Considerar agregar rate limiting al endpoint de login
- ⚠️ Implementar expiración de tokens y refresh tokens para producción
