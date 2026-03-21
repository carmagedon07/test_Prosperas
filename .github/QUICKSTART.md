# 🚀 Quick Start: Configuración CI/CD GitHub Actions

Guía rápida para activar el pipeline de deployment automático.

---

## ⚡ Configuración en 3 Pasos

### 1️⃣ Crear OIDC Provider en AWS

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 2️⃣ Crear IAM Role con Políticas

**a) Crear `trust-policy.json`:**

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

**b) Crear `permissions-policy.json`:**

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

**c) Ejecutar comandos:**

```bash
# Crear role
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://trust-policy.json

# Crear policy
aws iam create-policy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://permissions-policy.json

# Adjuntar policy al role
aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::521434189536:policy/GitHubActionsDeployPolicy

# Obtener ARN del role (cópialo para el siguiente paso)
aws iam get-role --role-name GitHubActionsDeployRole --query 'Role.Arn' --output text
```

### 3️⃣ Configurar GitHub Secret

1. Ve a: `https://github.com/TU_USUARIO/test_Prosperas/settings/secrets/actions`
2. Click en **New repository secret**
3. Agrega:
   - **Name:** `AWS_ROLE_ARN`
   - **Secret:** `arn:aws:iam::521434189536:role/GitHubActionsDeployRole`
4. Click en **Add secret**

---

## ✅ ¡Listo!

Ahora cuando hagas push a `main`, el workflow:

1. ✅ Detecta qué directorios cambiaron (`backend/`, `frontend/`, `worker/`)
2. ✅ Solo construye y sube las imágenes Docker que necesitan actualización
3. ✅ Despliega en orden: Backend → Worker → Frontend (con 3 min entre cada uno)
4. ✅ Verifica que el backend responda 200 en `/health`

**En PRs:** Solo ejecuta builds (sin deployment), para validación temprana.

---

## 🧪 Probar el Pipeline

```bash
# Hacer un cambio en backend
echo "# Test change" >> backend/README.md

# Commit y push
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main

# Ver el workflow en acción
# https://github.com/TU_USUARIO/test_Prosperas/actions
```

---

## 📚 Documentación Detallada

Para troubleshooting y explicaciones completas, consulta: [AWS_OIDC_SETUP.md](./AWS_OIDC_SETUP.md)

---

## 🔑 Información Importante

| Variable              | Valor                                                    |
|-----------------------|----------------------------------------------------------|
| **AWS Account ID**    | 521434189536                                             |
| **AWS Region**        | us-east-1                                                |
| **ECS Cluster**       | prospera-cluster                                         |
| **ECR Registry**      | 521434189536.dkr.ecr.us-east-1.amazonaws.com             |
| **ALB DNS**           | prospera-alb-246038476.us-east-1.elb.amazonaws.com       |
| **GitHub Repo**       | test_Prosperas (reemplaza TU_USUARIO con tu usuario)    |

**🔴 IMPORTANTE:** Reemplaza `TU_USUARIO` en `trust-policy.json` con tu usuario/organización real de GitHub.
