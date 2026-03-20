# ── Security Group: ALB ───────────────────────────────────────────────
# Acepta tráfico HTTP público → reenvía al backend ECS

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "HTTP ingress from internet to ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# ── Security Group: Backend ECS ───────────────────────────────────────
# Solo acepta tráfico del ALB en el puerto 8000

resource "aws_security_group" "backend" {
  name        = "${var.project_name}-backend-sg"
  description = "Backend ECS - accepts traffic only from ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "FastAPI from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "All outbound (DynamoDB, SQS, ECR via internet)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# ── Security Group: Worker ECS ────────────────────────────────────────
# Solo salida — los workers consumen SQS y escriben en DynamoDB (sin ingreso)

resource "aws_security_group" "worker" {
  name        = "${var.project_name}-worker-sg"
  description = "Worker ECS - outbound only (SQS + DynamoDB)"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}
