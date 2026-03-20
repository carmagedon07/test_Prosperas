# ── Application Load Balancer ─────────────────────────────────────────
# Expone el backend ECS con una URL pública (HTTP)
# Nota: HTTPS requiere un dominio + certificado ACM.
# Para el challenge usamos HTTP. Si se quiere HTTPS, se puede añadir
# un listener en puerto 443 con ACM + nombre de dominio en Route53.

resource "aws_lb" "backend" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids

  tags = local.common_tags
}

# ── Target Group ──────────────────────────────────────────────────────
# Apunta a las tasks ECS backend en el puerto 8000

resource "aws_lb_target_group" "backend" {
  name        = "${var.project_name}-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip" # requerido para ECS Fargate con awsvpc network mode

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }

  tags = local.common_tags
}

# ── HTTP Listener ─────────────────────────────────────────────────────

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.backend.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}
