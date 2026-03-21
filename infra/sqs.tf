# ============================================================
# SQS - Cola de mensajes para jobs
# ============================================================

# ── Dead Letter Queue ────────────────────────────────────────

resource "aws_sqs_queue" "jobs_dlq" {
  name                      = "${var.project_name}-${var.sqs_queue_name}-dlq"
  message_retention_seconds = 1209600 # 14 días

  tags = {
    Name = "${var.project_name}-jobs-dlq"
  }
}

# ── Cola Principal ───────────────────────────────────────────

resource "aws_sqs_queue" "jobs" {
  name                       = "${var.project_name}-${var.sqs_queue_name}"
  visibility_timeout_seconds = var.sqs_visibility_timeout
  message_retention_seconds  = var.sqs_message_retention
  receive_wait_time_seconds  = 20 # Long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.jobs_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-jobs-queue"
  }
}
