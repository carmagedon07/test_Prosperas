# ── SQS: Dead Letter Queue ────────────────────────────────────────────
# Recibe mensajes que fallaron 3 veces — estrategia de resiliencia ante fallos

resource "aws_sqs_queue" "jobs_dlq" {
  name                      = "${var.project_name}-jobs-dlq"
  message_retention_seconds = 1209600 # 14 días

  tags = local.common_tags
}

# ── SQS: Cola principal de jobs ───────────────────────────────────────

resource "aws_sqs_queue" "jobs" {
  name                       = "${var.project_name}-jobs-queue"
  visibility_timeout_seconds = 120   # tiempo para que el worker procese sin que otro lo tome
  message_retention_seconds  = 86400 # 1 día

  # DLQ: después de 3 reintentos fallidos, el mensaje va a la DLQ
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.jobs_dlq.arn
    maxReceiveCount     = 3
  })

  tags = local.common_tags
}
