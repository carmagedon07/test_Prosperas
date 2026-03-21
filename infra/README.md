# Infraestructura AWS con Terraform

Esta carpeta contiene la infraestructura como código (IaC) para desplegar la aplicación completa en AWS usando Terraform.

## 📦 Arquitectura Desplegada

- **VPC** con subnets públicas y privadas en 2 AZs
- **Application Load Balancer** (ALB) para exponer backend y frontend
- **ECS Fargate** para backend (FastAPI), frontend (React) y workers (SQS consumers)
- **SQS** con cola principal y Dead Letter Queue
- **DynamoDB** con tablas para jobs y usuarios
- **ECR** para almacenar imágenes Docker
- **CloudWatch** para logs centralizados
- **IAM** con permisos mínimos necesarios

## 🚀 Pasos para Desplegar

### 1. Configurar credenciales AWS

```powershell
$env:AWS_ACCESS_KEY_ID = "tu-access-key"
$env:AWS_SECRET_ACCESS_KEY = "tu-secret-key"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

### 2. Inicializar Terraform

```bash
cd infra
terraform init
```

### 3. Revisar el plan de ejecución

```bash
terraform plan -var="image_tag=latest"
```

### 4. Aplicar la infraestructura

```bash
terraform apply -var="image_tag=latest"
```

> ⚠️ **Importante**: Este comando creará recursos en AWS **que pueden generar costos**. Revisa el plan antes de confirmar.

### 5. Construir y publicar imágenes Docker a ECR

Una vez aplicada la infraestructura, Terraform mostrará los comandos exactos en el output `next_steps`. Ejemplo:

```bash
# Autenticarse en ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ecr-url>

# Backend
docker build -t <ecr-backend-url>:latest ./backend
docker push <ecr-backend-url>:latest

# Frontend  
docker build -t <ecr-frontend-url>:latest ./frontend
docker push <ecr-frontend-url>:latest

# Worker
docker build -t <ecr-worker-url>:latest ./worker
docker push <ecr-worker-url>:latest
```

### 6. Forzar despliegue de servicios ECS

```bash
aws ecs update-service --cluster prospera-cluster --service prospera-backend --force-new-deployment
aws ecs update-service --cluster prospera-cluster --service prospera-frontend --force-new-deployment
aws ecs update-service --cluster prospera-cluster --service prospera-worker --force-new-deployment
```

## 🔧 Personalización

### Variables principales

Puedes personalizar la infraestructura editando `variables.tf` o pasando variables en la línea de comandos:

```bash
terraform apply \
  -var="project_name=mi-proyecto" \
  -var="environment=staging" \
  -var="workers_desired_count=3" \
  -var="jwt_secret=mi-secreto-super-seguro"
```

### Variables más comunes

| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `project_name` | Nombre del proyecto | `prospera` |
| `aws_region` | Región de AWS | `us-east-1` |
| `backend_desired_count` | Número de instancias backend | `1` |
| `workers_desired_count` | Número de workers concurrentes | `2` |
| `jwt_secret` | Secreto para firmar JWTs | ⚠️ cambiar en prod |
| `image_tag` | Tag de las imágenes Docker | `latest` |

### Usar archivo de variables

Crea un archivo `terraform.tfvars`:

```hcl
project_name         = "mi-proyecto"
environment          = "production"
workers_desired_count = 3
jwt_secret           = "un-secreto-muy-largo-y-aleatorio-123456"
```

Luego aplica sin especificar variables:

```bash
terraform apply
```

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# Backend
aws logs tail /ecs/prospera/backend --follow

# Workers
aws logs tail /ecs/prospera/worker --follow
```

### Estado de servicios ECS

```bash
aws ecs describe-services \
  --cluster prospera-cluster \
  --services prospera-backend prospera-worker \
  --query 'services[*].[serviceName,desiredCount,runningCount,status]' \
  --output table
```

### Mensajes en cola SQS

```bash
aws sqs get-queue-attributes \
  --queue-url $(terraform output -raw sqs_queue_url) \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
```

## 🧹 Limpieza (Destruir Recursos)

Para eliminar **todos los recursos** creados:

```bash
terraform destroy -var="image_tag=latest"
```

> ⚠️ Esto eliminará **permanentemente** todas las tablas DynamoDB, colas SQS, imágenes ECR, etc.

## 📁 Estructura de Archivos

```
infra/
├── providers.tf          → Configuración del provider AWS
├── variables.tf          → Variables de entrada
├── outputs.tf            → Outputs útiles post-despliegue
├── vpc.tf                → VPC, subnets, internet gateway
├── security_groups.tf    → Security groups para ALB, ECS
├── alb.tf                → Application Load Balancer
├── sqs.tf                → Cola SQS + DLQ
├── dynamodb.tf           → Tablas jobs y users
├── ecr.tf                → Repositorios Docker
├── iam.tf                → Roles y políticas IAM
├── cloudwatch.tf         → Log groups
├── ecs_cluster.tf        → Cluster ECS Fargate
├── ecs_backend.tf        → Backend FastAPI
├── ecs_frontend.tf       → Frontend React
└── ecs_workers.tf        → Workers SQS consumers
```

## 🔒 Seguridad

- **JWT_SECRET**: Cambia el valor por defecto en producción usando `-var="jwt_secret=..."`
- **IAM Roles**: Los permisos siguen el principio de mínimo privilegio
- **Security Groups**: Solo puertos necesarios abiertos
- **Imágenes ECR**: Escaneo automático de vulnerabilidades habilitado
- **HTTPS**: Por defecto usa HTTP (puerto 80). Para HTTPS necesitas:
  - Certificado en AWS Certificate Manager (ACM)
  - Dominio en Route 53 o DNS externo
  - Modificar `alb.tf` para añadir listener 443

## 🆘 Troubleshooting

### Las tareas ECS no arrancan

```bash
# Ver eventos del servicio
aws ecs describe-services --cluster prospera-cluster --services prospera-backend \
  --query 'services[0].events[:5]' --output table

# Ver tareas fallidas
aws ecs list-tasks --cluster prospera-cluster --service-name prospera-backend --desired-status STOPPED
```

### Backend devuelve 503

- Verificar que los health checks pasen: `/health` debe retornar 200
- Revisar los logs de CloudWatch
- Confirmar que la imagen Docker está disponible en ECR

### Workers no consumen mensajes de SQS

- Verificar permisos IAM en `iam.tf`
- Revisar logs: `aws logs tail /ecs/prospera/worker --follow`
- Confirmar que `SQS_QUEUE_NAME` se pasa correctamente como variable de entorno

## 📚 Recursos

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
