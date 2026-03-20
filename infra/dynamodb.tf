# ── DynamoDB Tables ───────────────────────────────────────────────────

# Tabla principal de jobs
resource "aws_dynamodb_table" "jobs" {
  name         = "${var.project_name}-jobs"
  billing_mode = "PAY_PER_REQUEST" # free tier: 200M req/mes — sin costo para el challenge
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # GSI para listar jobs por usuario eficientemente (GET /jobs)
  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  tags = local.common_tags
}

# Tabla de usuarios (auth)
resource "aws_dynamodb_table" "users" {
  name         = "${var.project_name}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = local.common_tags
}
