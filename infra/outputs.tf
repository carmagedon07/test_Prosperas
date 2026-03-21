# ============================================================
# Outputs - Información útil post-despliegue
# ============================================================

# ── Networking ───────────────────────────────────────────────

output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs de las subnets públicas"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs de las subnets privadas"
  value       = aws_subnet.private[*].id
}

# ── Load Balancer ────────────────────────────────────────────

output "alb_dns_name" {
  description = "DNS público del Application Load Balancer"
  value       = aws_lb.app.dns_name
}

output "alb_url" {
  description = "URL completa del ALB"
  value       = "http://${aws_lb.app.dns_name}"
}

output "backend_url" {
  description = "URL del backend (via ALB)"
  value       = "http://${aws_lb.app.dns_name}/api"
}

output "frontend_url" {
  description = "URL del frontend (via ALB)"
  value       = "http://${aws_lb.app.dns_name}"
}

# ── SQS ──────────────────────────────────────────────────────

output "sqs_queue_url" {
  description = "URL de la cola SQS de jobs"
  value       = aws_sqs_queue.jobs.url
}

output "sqs_queue_arn" {
  description = "ARN de la cola SQS de jobs"
  value       = aws_sqs_queue.jobs.arn
}

output "sqs_queue_name" {
  description = "Nombre de la cola SQS"
  value       = aws_sqs_queue.jobs.name
}

output "sqs_dlq_url" {
  description = "URL de la Dead Letter Queue"
  value       = aws_sqs_queue.jobs_dlq.url
}

# ── DynamoDB ─────────────────────────────────────────────────

output "dynamodb_jobs_table_name" {
  description = "Nombre de la tabla DynamoDB de jobs"
  value       = aws_dynamodb_table.jobs.name
}

output "dynamodb_jobs_table_arn" {
  description = "ARN de la tabla DynamoDB de jobs"
  value       = aws_dynamodb_table.jobs.arn
}

output "dynamodb_users_table_name" {
  description = "Nombre de la tabla DynamoDB de usuarios"
  value       = aws_dynamodb_table.users.name
}

output "dynamodb_users_table_arn" {
  description = "ARN de la tabla DynamoDB de usuarios"
  value       = aws_dynamodb_table.users.arn
}

# ── ECR ──────────────────────────────────────────────────────

output "ecr_backend_url" {
  description = "URL del repositorio ECR del backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "URL del repositorio ECR del frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_worker_url" {
  description = "URL del repositorio ECR del worker"
  value       = aws_ecr_repository.worker.repository_url
}

# ── ECS ──────────────────────────────────────────────────────

output "ecs_cluster_name" {
  description = "Nombre del cluster ECS"
  value       = aws_ecs_cluster.main.name
}

output "ecs_backend_service_name" {
  description = "Nombre del servicio ECS del backend"
  value       = aws_ecs_service.backend.name
}

output "ecs_frontend_service_name" {
  description = "Nombre del servicio ECS del frontend"
  value       = aws_ecs_service.frontend.name
}

output "ecs_worker_service_name" {
  description = "Nombre del servicio ECS de workers"
  value       = aws_ecs_service.worker.name
}

# ── CloudWatch ───────────────────────────────────────────────

output "cloudwatch_backend_log_group" {
  description = "CloudWatch Log Group del backend"
  value       = aws_cloudwatch_log_group.backend.name
}

output "cloudwatch_worker_log_group" {
  description = "CloudWatch Log Group de workers"
  value       = aws_cloudwatch_log_group.worker.name
}

# ── Comandos útiles ──────────────────────────────────────────

output "next_steps" {
  description = "Próximos pasos para completar el despliegue"
  value = <<-EOT
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║           DESPLIEGUE COMPLETADO - PRÓXIMOS PASOS             ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    1️⃣  Construir y publicar imágenes Docker a ECR:
    
       # Backend
       aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.backend.repository_url}
       docker build -t ${aws_ecr_repository.backend.repository_url}:${var.image_tag} ./backend
       docker push ${aws_ecr_repository.backend.repository_url}:${var.image_tag}
       
       # Frontend
       docker build -t ${aws_ecr_repository.frontend.repository_url}:${var.image_tag} ./frontend
       docker push ${aws_ecr_repository.frontend.repository_url}:${var.image_tag}
       
       # Worker
       docker build -t ${aws_ecr_repository.worker.repository_url}:${var.image_tag} ./worker
       docker push ${aws_ecr_repository.worker.repository_url}:${var.image_tag}
    
    2️⃣  Forzar nuevo despliegue de servicios ECS:
    
       aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.backend.name} --force-new-deployment --region ${var.aws_region}
       aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.frontend.name} --force-new-deployment --region ${var.aws_region}
       aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.worker.name} --force-new-deployment --region ${var.aws_region}
    
    3️⃣  Acceder a la aplicación:
    
       Frontend: http://${aws_lb.app.dns_name}
       Backend:  http://${aws_lb.app.dns_name}/api
       Health:   http://${aws_lb.app.dns_name}/health
    
    4️⃣  Monitorear logs:
    
       aws logs tail /ecs/${var.project_name}/backend --follow --region ${var.aws_region}
       aws logs tail /ecs/${var.project_name}/worker --follow --region ${var.aws_region}
    
    5️⃣  Ver estado de servicios ECS:
    
       aws ecs describe-services --cluster ${aws_ecs_cluster.main.name} --services ${aws_ecs_service.backend.name} --region ${var.aws_region}
    
    ═══════════════════════════════════════════════════════════════
  EOT
}
