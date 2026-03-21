# ☑️ Checklist de Configuración CI/CD

Usa este checklist para asegurarte de completar todos los pasos necesarios.

---

## 📋 Pre-requisitos

- [ ] Tengo acceso a la consola AWS con permisos de IAM
- [ ] Tengo AWS CLI instalado y configurado
- [ ] Tengo acceso de admin al repositorio GitHub `test_Prosperas`
- [ ] La infraestructura de Terraform está desplegada en AWS (ECS, ECR, ALB)

---

## 🔐 Configuración AWS (OIDC)

### Paso 1: OIDC Provider

- [ ] Ejecuté el comando para crear OIDC Provider
- [ ] Verifiqué que se creó con: `aws iam list-open-id-connect-providers`
- [ ] El output muestra: `token.actions.githubusercontent.com`

### Paso 2: IAM Policies

- [ ] Creé el archivo `trust-policy.json`
- [ ] **IMPORTANTE:** Reemplacé `TU_USUARIO` con mi usuario/org de GitHub
- [ ] Creé el archivo `permissions-policy.json`
- [ ] Ambos archivos JSON tienen sintaxis válida (sin comas extra)

### Paso 3: IAM Role

- [ ] Ejecuté `aws iam create-role` con trust-policy.json
- [ ] Ejecuté `aws iam create-policy` con permissions-policy.json
- [ ] Ejecuté `aws iam attach-role-policy` para adjuntar la policy
- [ ] Copié el ARN del role (salida del comando `get-role`)

**ARN copiado:** `_________________________________`

---

## 🐙 Configuración GitHub

### Paso 4: GitHub Secret

- [ ] Fui a `Settings` → `Secrets and variables` → `Actions`
- [ ] Clickeé en `New repository secret`
- [ ] Nombre: `AWS_ROLE_ARN`
- [ ] Valor: El ARN que copié en el paso anterior
- [ ] Clickeé en `Add secret`
- [ ] Verifiqué que aparece en la lista de secrets

---

## 🧪 Verificación

### Paso 5: Primer Deployment

- [ ] Hice un cambio menor en `backend/`, `frontend/` o `worker/`
- [ ] Hice commit: `git commit -m "test: verificar CI/CD"`
- [ ] Hice push: `git push origin main`
- [ ] Fui a la pestaña `Actions` en GitHub
- [ ] Veo un workflow ejecutándose
- [ ] El job `changes` completó correctamente
- [ ] Los jobs `build-*` completaron sin errores
- [ ] Los jobs `deploy-*` actualizaron los servicios ECS
- [ ] El job `health-check` pasó (status 200)

### Paso 6: Verificar en AWS

- [ ] Ejecuté: `aws ecs describe-services --cluster prospera-cluster --services prospera-backend`
- [ ] El servicio muestra `status: ACTIVE` y `runningCount: 1`
- [ ] Ejecuté: `curl http://prospera-alb-246038476.us-east-1.elb.amazonaws.com/health`
- [ ] La respuesta es: `{"status":"ok","service":"backend"}`

---

## 🎯 Funcionalidades a Probar

### Path-based Optimization

- [ ] Cambié solo `backend/main.py` → Solo `build-backend` y `deploy-backend` ejecutaron
- [ ] Cambié solo `frontend/src/App.js` → Solo `build-frontend` y `deploy-frontend` ejecutaron
- [ ] Cambié solo `worker/main.py` → Solo `build-worker` y `deploy-worker` ejecutaron

### Pull Request Validation

- [ ] Creé una rama: `git checkout -b test-pr`
- [ ] Hice un cambio y push: `git push origin test-pr`
- [ ] Creé un PR en GitHub
- [ ] El workflow ejecutó solo los jobs `build-*` (sin `deploy-*`)
- [ ] El PR muestra checks pasados ✅

### Sequential Deployment

- [ ] Cambié `backend/` y `worker/` simultáneamente
- [ ] El workflow desplegó Backend → Worker en orden
- [ ] Cada servicio esperó 3 minutos + stabilization antes del siguiente

### Health Check Failure

- [ ] (Opcional) Rompí el backend intencionalmente
- [ ] El workflow falló en el job `health-check`
- [ ] Recibí notificación de failure en GitHub

---

## ✅ Checklist General

- [ ] ✅ OIDC Provider creado en AWS
- [ ] ✅ IAM Role `GitHubActionsDeployRole` existe
- [ ] ✅ IAM Policy `GitHubActionsDeployPolicy` adjunta
- [ ] ✅ GitHub Secret `AWS_ROLE_ARN` configurado
- [ ] ✅ Workflow ejecuta correctamente en push a `main`
- [ ] ✅ Workflow ejecuta builds en Pull Requests
- [ ] ✅ Health check verifica deployment exitoso
- [ ] ✅ Solo se construyen las imágenes con cambios

---

## 🚨 Troubleshooting

Si algo falla, consulta:
- [QUICKSTART.md](./QUICKSTART.md) - Guía rápida de configuración
- [AWS_OIDC_SETUP.md](./AWS_OIDC_SETUP.md) - Documentación detallada con troubleshooting

---

## 📝 Notas

```
Fecha de configuración: _______________

Problemas encontrados:
- 
- 

Soluciones aplicadas:
- 
- 
```

---

## 🎉 ¡Configuración Completa!

Una vez que todos los items estén marcados, tu CI/CD está funcionando completamente.

**Próximos pasos sugeridos:**
1. Configurar branch protection rules en `main` (requiere PR reviews)
2. Agregar notificaciones de Slack/Discord para deployments
3. Implementar rollback automático en caso de failure
4. Agregar environment específico para staging vs production
