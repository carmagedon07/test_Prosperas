# ============================================================
# DynamoDB - Tablas para jobs y usuarios
# ============================================================

# ── Tabla Jobs ───────────────────────────────────────────────

resource "aws_dynamodb_table" "jobs" {
  name         = "${var.project_name}-${var.jobs_table_name}"
  billing_mode = "PAY_PER_REQUEST" # On-demand pricing
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # GSI para consultar jobs por usuario
  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  tags = {
    Name = "${var.project_name}-jobs-table"
  }
}

# ── Tabla Users ──────────────────────────────────────────────

resource "aws_dynamodb_table" "users" {
  name         = "${var.project_name}-${var.users_table_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-users-table"
  }
}
