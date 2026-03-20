# ── CloudWatch Log Groups ─────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}/backend"
  retention_in_days = 7
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}/worker"
  retention_in_days = 7
  tags              = local.common_tags
}

# ── ECS Cluster ───────────────────────────────────────────────────────

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
  tags = local.common_tags
}

# ── Backend Task Definition ───────────────────────────────────────────
# 0.25 vCPU + 512 MB RAM — suficiente para FastAPI con tráfico de prueba

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "backend"
    image = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "AWS_REGION",          value = var.aws_region },
      { name = "JOBS_TABLE_NAME",     value = aws_dynamodb_table.jobs.name },
      { name = "USERS_TABLE_NAME",    value = aws_dynamodb_table.users.name },
      { name = "SQS_QUEUE_NAME",      value = aws_sqs_queue.jobs.name },
      { name = "JWT_EXPIRY_MINUTES",  value = tostring(var.jwt_expiry_minutes) },
      # Sin SQS_ENDPOINT ni DYNAMODB_ENDPOINT → boto3 usa los endpoints reales de AWS
    ]

    # JWT_SECRET se lee de SSM Parameter Store en tiempo de ejecución
    secrets = [{
      name      = "JWT_SECRET"
      valueFrom = aws_ssm_parameter.jwt_secret.arn
    }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.backend.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "backend"
      }
    }

    essential   = true
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 30
    }
  }])

  tags = local.common_tags
}

# ── Worker Task Definition ────────────────────────────────────────────
# Mismo sizing que el backend. desired_count=2 da los 2 workers concurrentes.

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "worker"
    image = "${aws_ecr_repository.worker.repository_url}:${var.image_tag}"

    environment = [
      { name = "AWS_REGION",       value = var.aws_region },
      { name = "JOBS_TABLE_NAME",  value = aws_dynamodb_table.jobs.name },
      { name = "USERS_TABLE_NAME", value = aws_dynamodb_table.users.name },
      { name = "SQS_QUEUE_NAME",   value = aws_sqs_queue.jobs.name },
      # Sin SQS_ENDPOINT ni DYNAMODB_ENDPOINT → boto3 usa AWS real
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.worker.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "worker"
      }
    }

    essential = true
  }])

  tags = local.common_tags
}

# ── Backend ECS Service ───────────────────────────────────────────────
# 1 tarea detrás del ALB

resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.backend.id]
    assign_public_ip = true # necesario en default VPC (sin NAT gateway)
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  # Esperar a que el listener esté creado antes de registrar al target group
  depends_on = [aws_lb_listener.http]

  # Evita que Terraform destruya el servicio si el deploy falla a mitad
  lifecycle {
    ignore_changes = [task_definition]
  }

  tags = local.common_tags
}

# ── Worker ECS Service ────────────────────────────────────────────────
# 2 tareas = 2 workers corriendo en paralelo (requisito del challenge)

resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 2 # <= mínimo 2 mensajes en paralelo
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.worker.id]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

  tags = local.common_tags
}
