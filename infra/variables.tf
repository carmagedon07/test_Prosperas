# ============================================================
# Variables de configuración
# ============================================================

# ── General ──────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region donde desplegar la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nombre del proyecto (usado para nombrar recursos)"
  type        = string
  default     = "prospera"
}

variable "environment" {
  description = "Entorno de despliegue"
  type        = string
  default     = "staging"
}

# ── Networking ───────────────────────────────────────────────

variable "vpc_cidr" {
  description = "CIDR block para la VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks para subnets públicas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks para subnets privadas"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "availability_zones" {
  description = "Availability Zones a utilizar"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ── ECS / Fargate ────────────────────────────────────────────

variable "backend_cpu" {
  description = "CPU para el backend (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Memoria para el backend en MB"
  type        = number
  default     = 512
}

variable "backend_desired_count" {
  description = "Número de tareas backend deseadas"
  type        = number
  default     = 1
}

variable "frontend_cpu" {
  description = "CPU para el frontend"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Memoria para el frontend en MB"
  type        = number
  default     = 512
}

variable "frontend_desired_count" {
  description = "Número de tareas frontend deseadas"
  type        = number
  default     = 1
}

variable "worker_cpu" {
  description = "CPU para cada worker"
  type        = number
  default     = 256
}

variable "worker_memory" {
  description = "Memoria para cada worker en MB"
  type        = number
  default     = 512
}

variable "workers_desired_count" {
  description = "Número de workers concurrentes (worker-1, worker-2, etc.)"
  type        = number
  default     = 2
}

variable "image_tag" {
  description = "Tag de las imágenes Docker en ECR"
  type        = string
  default     = "latest"
}

# ── JWT Configuration ────────────────────────────────────────

variable "jwt_secret" {
  description = "Secret para firmar tokens JWT (cambiar en producción)"
  type        = string
  sensitive   = true
  default     = "cambia-esto-por-un-secreto-seguro-en-produccion"
}

variable "jwt_expiry_minutes" {
  description = "Tiempo de expiración del JWT en minutos"
  type        = number
  default     = 60
}

# ── SQS Configuration ────────────────────────────────────────

variable "sqs_queue_name" {
  description = "Nombre de la cola SQS"
  type        = string
  default     = "jobs-queue"
}

variable "sqs_visibility_timeout" {
  description = "Visibility timeout en segundos"
  type        = number
  default     = 300
}

variable "sqs_message_retention" {
  description = "Tiempo de retención de mensajes en segundos"
  type        = number
  default     = 345600 # 4 días
}

# ── DynamoDB Configuration ───────────────────────────────────

variable "jobs_table_name" {
  description = "Nombre de la tabla DynamoDB para jobs"
  type        = string
  default     = "jobs"
}

variable "users_table_name" {
  description = "Nombre de la tabla DynamoDB para usuarios"
  type        = string
  default     = "users"
}
