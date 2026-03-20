# ── SSM Parameter Store ───────────────────────────────────────────────
# Los secretos se almacenan encriptados en SSM y se inyectan al contenedor
# en tiempo de ejecución — nunca hardcodeados en la imagen Docker.

resource "aws_ssm_parameter" "jwt_secret" {
  name        = "/${var.project_name}/jwt-secret"
  description = "JWT secret key for signing authentication tokens"
  type        = "SecureString"
  value       = var.jwt_secret

  tags = local.common_tags
}

# Permisos para que el ECS task execution role lea el secreto de SSM
resource "aws_iam_role_policy" "ecs_execution_ssm" {
  name = "${var.project_name}-ecs-execution-ssm"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameters", "ssm:GetParameter"]
      Resource = [aws_ssm_parameter.jwt_secret.arn]
    }]
  })
}
