# Configuración de OIDC para GitHub Actions en AWS

Este documento contiene los pasos detallados para configurar OIDC (OpenID Connect) entre GitHub Actions y AWS, permitiendo autenticación segura sin usar credenciales de larga duración.

## 📋 Tabla de Contenidos

1. [¿Por qué OIDC?](#por-qué-oidc)
2. [Prerequisitos](#prerequisitos)
3. [Paso 1: Crear OIDC Provider en AWS](#paso-1-crear-oidc-provider-en-aws)
4. [Paso 2: Crear IAM Role con Política Mínima](#paso-2-crear-iam-role-con-política-mínima)
5. [Paso 3: Configurar GitHub Secrets](#paso-3-configurar-github-secrets)
6. [Paso 4: Verificar Configuración](#paso-4-verificar-configuración)
7. [Troubleshooting](#troubleshooting)

---

## ¿Por qué OIDC?

OIDC es más seguro que usar Access Keys porque:
- ✅ No hay credenciales de larga duración almacenadas en GitHub
- ✅ Los tokens son temporales (expiran automáticamente)
- ✅ Puedes limitar qué repositorios/branches pueden asumir el role
- ✅ Cumple con las mejores prácticas de seguridad de AWS

---

## Prerequisitos

- Cuenta de AWS con permisos para crear IAM Roles y Providers
- Repositorio GitHub: `test_Prosperas` (o tu usuario/repositorio real)
- AWS CLI instalado y configurado (opcional, puede hacerse desde consola)

---

## Paso 1: Crear OIDC Provider en AWS

### Opción A: Desde AWS CLI (Recomendado)

```bash
# 1. Crear el OIDC Provider para GitHub
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --tags Key=Name,Value=GitHubActionsOIDC

# 2. Verificar que se creó correctamente
aws iam list-open-id-connect-providers
```

**Nota:** El thumbprint `6938fd4d98bab03faadb97b34396831e3780aea1` es el certificado actual de GitHub Actions OIDC (válido hasta 2031).

### Opción B: Desde AWS Console

1. Ve a **IAM Console** → **Identity providers** → **Add provider**
2. Selecciona **OpenID Connect**
3. Ingresa los siguientes valores:
   - **Provider URL:** `https://token.actions.githubusercontent.com`
   - Click en **Get thumbprint** (se auto-detecta)
   - **Audience:** `sts.amazonaws.com`
4. Click en **Add provider**

---

## Paso 2: Crear IAM Role con Política Mínima

### 2.1: Crear Trust Policy para el Role

Crea un archivo `trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::521434189536:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:TU_USUARIO/test_Prosperas:*"
        }
      }
    }
  ]
}
```

**IMPORTANTE:** Reemplaza `TU_USUARIO` con tu usuario/organización de GitHub real.

**Condiciones de seguridad:**
- `StringEquals`: Solo permite tokens de GitHub Actions destinados a AWS STS
- `StringLike`: Solo permite tu repositorio específico en cualquier branch (`*`)
- Para limitar a `main` solamente, usa: `"repo:TU_USUARIO/test_Prosperas:ref:refs/heads/main"`

### 2.2: Crear Permissions Policy (Permisos Mínimos)

Crea un archivo `permissions-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRPermissions",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECSDeployPermissions",
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTasks"
      ],
      "Resource": [
        "arn:aws:ecs:us-east-1:521434189536:service/prospera-cluster/prospera-backend",
        "arn:aws:ecs:us-east-1:521434189536:service/prospera-cluster/prospera-worker",
        "arn:aws:ecs:us-east-1:521434189536:service/prospera-cluster/prospera-frontend"
      ]
    }
  ]
}
```

**Explicación de permisos:**
- **ECR:** Push de imágenes Docker (Resource: `*` porque ECR requiere permisos globales para auth)
- **ECS:** Update de servicios específicos solamente (scope limitado a tus 3 servicios)

### 2.3: Crear el Role con las Políticas

```bash
# 1. Crear el IAM Role con la trust policy
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://trust-policy.json \
  --description "Role for GitHub Actions to deploy to ECS"

# 2. Crear la custom policy
aws iam create-policy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://permissions-policy.json \
  --description "Minimal permissions for GitHub Actions: ECR push + ECS deploy"

# 3. Adjuntar la policy al role
aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::521434189536:policy/GitHubActionsDeployPolicy

# 4. Obtener el ARN del role (lo necesitarás para GitHub Secrets)
aws iam get-role --role-name GitHubActionsDeployRole --query 'Role.Arn' --output text
```

**Output esperado:**
```
arn:aws:iam::521434189536:role/GitHubActionsDeployRole
```

Guarda este ARN, lo usarás en el siguiente paso.

---

## Paso 3: Configurar GitHub Secrets

Ve a tu repositorio GitHub: `https://github.com/TU_USUARIO/test_Prosperas/settings/secrets/actions`

Agrega el siguiente **Secret**:

| Secret Name       | Value                                                                  | Descripción                              |
|-------------------|------------------------------------------------------------------------|------------------------------------------|
| `AWS_ROLE_ARN`    | `arn:aws:iam::521434189536:role/GitHubActionsDeployRole`              | ARN del role OIDC que acabas de crear   |

**No necesitas agregar `AWS_ACCESS_KEY_ID` ni `AWS_SECRET_ACCESS_KEY` con OIDC.**

---

## Paso 4: Verificar Configuración

### 4.1: Hacer un Push de Prueba

1. Modifica cualquier archivo en `backend/`, `frontend/` o `worker/`
2. Haz commit y push a `main`:

```bash
git add .
git commit -m "test: verificar OIDC deployment"
git push origin main
```

3. Ve a la pestaña **Actions** en GitHub
4. El workflow debería ejecutarse automáticamente

### 4.2: Verificar Logs

En los logs del workflow, busca:
- ✅ `Configure AWS credentials (OIDC)` debe completarse sin errores
- ✅ `Login to Amazon ECR` debe mostrar `Login Succeeded`
- ✅ `Build and push` debe subir imágenes a ECR
- ✅ `Deploy` debe actualizar los servicios ECS

---

## Troubleshooting

### Error: "Not authorized to perform sts:AssumeRoleWithWebIdentity"

**Causa:** El trust policy no coincide con tu repositorio.

**Solución:**
1. Verifica que el usuario/org en `trust-policy.json` sea correcto
2. Actualiza el trust policy:
   ```bash
   aws iam update-assume-role-policy \
     --role-name GitHubActionsDeployRole \
     --policy-document file://trust-policy.json
   ```

### Error: "User is not authorized to perform ecr:PutImage"

**Causa:** La permissions policy no está adjunta o es incorrecta.

**Solución:**
1. Verifica que la policy esté adjunta:
   ```bash
   aws iam list-attached-role-policies --role-name GitHubActionsDeployRole
   ```
2. Si no aparece, adjúntala:
   ```bash
   aws iam attach-role-policy \
     --role-name GitHubActionsDeployRole \
     --policy-arn arn:aws:iam::521434189536:policy/GitHubActionsDeployPolicy
   ```

### Error: "An error occurred (InvalidIdentityToken)"

**Causa:** El OIDC provider no está creado o tiene el thumbprint incorrecto.

**Solución:**
1. Verifica que el provider existe:
   ```bash
   aws iam list-open-id-connect-providers
   ```
2. Si no existe, créalo (ver Paso 1)

### Workflow se salta todos los jobs

**Causa:** No se detectaron cambios en `backend/`, `frontend/` o `worker/`

**Solución:**
- Esto es normal. El workflow solo construye/despliega lo que cambió
- Para forzar rebuild, modifica un archivo en el directorio correspondiente
- Para PRs, solo hace build (no deploy), es esperado

---

## Resumen de Recursos Creados

| Recurso                              | ARN/Identificador                                                     |
|--------------------------------------|-----------------------------------------------------------------------|
| OIDC Provider                         | `arn:aws:iam::521434189536:oidc-provider/token.actions.githubusercontent.com` |
| IAM Role                              | `arn:aws:iam::521434189536:role/GitHubActionsDeployRole`            |
| IAM Policy                            | `arn:aws:iam::521434189536:policy/GitHubActionsDeployPolicy`        |

---

## Próximos Pasos

1. ✅ Workflow configurado en `.github/workflows/deploy.yml`
2. ✅ OIDC Provider creado
3. ✅ IAM Role con permisos mínimos
4. ✅ GitHub Secret configurado
5. 🎯 **Próximo:** Hacer push a `main` y observar el deployment automático

---

## Comandos Útiles

```bash
# Ver estado de los servicios ECS
aws ecs describe-services \
  --cluster prospera-cluster \
  --services prospera-backend prospera-frontend prospera-worker

# Ver últimas tareas del backend
aws ecs list-tasks \
  --cluster prospera-cluster \
  --service-name prospera-backend

# Ver logs del deployment
aws logs tail /ecs/prospera-backend --follow

# Health check manual
curl http://prospera-alb-246038476.us-east-1.elb.amazonaws.com/health
```
