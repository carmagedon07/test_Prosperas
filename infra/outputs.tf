output "backend_url" {
  description = "URL pública de la API (ALB). Úsala como REACT_APP_API_URL."
  value       = "http://${aws_lb.backend.dns_name}"
}

output "frontend_url" {
  description = "URL pública del frontend (CloudFront HTTPS)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "ecr_backend_url" {
  description = "URL del repositorio ECR del backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_worker_url" {
  description = "URL del repositorio ECR del worker"
  value       = aws_ecr_repository.worker.repository_url
}

output "sqs_queue_url" {
  description = "URL de la cola SQS de jobs"
  value       = aws_sqs_queue.jobs.url
}

output "s3_frontend_bucket" {
  description = "Nombre del bucket S3 para el frontend"
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_distribution_id" {
  description = "ID de la distribución CloudFront (necesario para invalidaciones en CI/CD)"
  value       = aws_cloudfront_distribution.frontend.id
}

output "ecs_cluster_name" {
  description = "Nombre del cluster ECS"
  value       = aws_ecs_cluster.main.name
}

output "jobs_table_name" {
  description = "Nombre de la tabla DynamoDB de jobs"
  value       = aws_dynamodb_table.jobs.name
}

output "users_table_name" {
  description = "Nombre de la tabla DynamoDB de users"
  value       = aws_dynamodb_table.users.name
}
