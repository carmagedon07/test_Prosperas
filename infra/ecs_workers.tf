# ============================================================
# ECS Workers - Consumidores SQS concurrentes
# ============================================================

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "worker"
      image = "${aws_ecr_repository.worker.repository_url}:${var.image_tag}"

      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "SQS_QUEUE_NAME", value = aws_sqs_queue.jobs.name },
        { name = "JOBS_TABLE_NAME", value = aws_dynamodb_table.jobs.name },
        { name = "USERS_TABLE_NAME", value = aws_dynamodb_table.users.name },
        { name = "JWT_SECRET", value = var.jwt_secret },
        { name = "JWT_EXPIRY_MINUTES", value = tostring(var.jwt_expiry_minutes) },
        { name = "WORKER_CONCURRENCY", value = "4" },
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
    }
  ])

  tags = {
    Name = "${var.project_name}-worker-task"
  }
}

resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.workers_desired_count # 2 workers concurrentes
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.worker.id]
    assign_public_ip = true
  }

  depends_on = [
    aws_iam_role_policy.ecs_task_dynamodb,
    aws_iam_role_policy.ecs_task_sqs,
  ]

  lifecycle {
    ignore_changes = [task_definition]
  }

  tags = {
    Name = "${var.project_name}-worker-service"
  }
}
