# ============================================================
# Security Groups
# ============================================================

# ── ALB Security Group ───────────────────────────────────────

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group para Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP desde Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS desde Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-alb-sg"
  }
}

# ── Backend Security Group ───────────────────────────────────

resource "aws_security_group" "backend" {
  name        = "${var.project_name}-backend-sg"
  description = "Security group para backend FastAPI"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "FastAPI desde ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "All outbound traffic (DynamoDB, SQS, ECR)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-backend-sg"
  }
}

# ── Frontend Security Group ──────────────────────────────────

resource "aws_security_group" "frontend" {
  name        = "${var.project_name}-frontend-sg"
  description = "Security group para frontend React"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "React desde ALB"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-frontend-sg"
  }
}

# ── Workers Security Group ───────────────────────────────────

resource "aws_security_group" "worker" {
  name        = "${var.project_name}-worker-sg"
  description = "Security group para workers SQS (solo egress)"
  vpc_id      = aws_vpc.main.id

  # Sin reglas de ingress - los workers solo consumen de SQS y escriben a DynamoDB

  egress {
    description = "All outbound traffic (SQS, DynamoDB)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-worker-sg"
  }
}
