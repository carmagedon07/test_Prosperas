# ============================================================
# CloudWatch - Log Groups para ECS
# ============================================================

# ── Backend Logs ─────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}/backend"
  retention_in_days = 7 # Ajustar según necesidades (1, 3, 7, 14, 30, etc.)

  tags = {
    Name = "${var.project_name}-backend-logs"
  }
}

# ── Frontend Logs ────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${var.project_name}/frontend"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-frontend-logs"
  }
}

# ── Worker Logs ──────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}/worker"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-worker-logs"
  }
}
