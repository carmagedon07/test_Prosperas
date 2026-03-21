# ============================================================
# ECS Frontend - React (puerto 3000)
# ============================================================

resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.project_name}-frontend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.frontend_cpu
  memory                   = var.frontend_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = "${aws_ecr_repository.frontend.repository_url}:${var.image_tag}"

      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        # La URL del backend será la del ALB
        { name = "REACT_APP_API_URL", value = "http://${aws_lb.app.dns_name}" },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "frontend"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name = "${var.project_name}-frontend-task"
  }
}

resource "aws_ecs_service" "frontend" {
  name            = "${var.project_name}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = var.frontend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.frontend.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.http]

  lifecycle {
    ignore_changes = [task_definition]
  }

  tags = {
    Name = "${var.project_name}-frontend-service"
  }
}
