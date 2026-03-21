# ============================================================
# IAM - Roles y políticas para ECS Fargate
# ============================================================

# ── ECS Task Execution Role ──────────────────────────────────
# Permite a ECS: pull de imágenes ECR + envío de logs a CloudWatch

data "aws_iam_policy_document" "ecs_task_execution_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name               = "${var.project_name}-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume.json

  tags = {
    Name = "${var.project_name}-ecs-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ── ECS Task Role ────────────────────────────────────────────
# Permite a la aplicación: acceso a DynamoDB y SQS

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task" {
  name               = "${var.project_name}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json

  tags = {
    Name = "${var.project_name}-ecs-task-role"
  }
}

# ── Política: DynamoDB Access ────────────────────────────────

data "aws_iam_policy_document" "dynamodb_access" {
  statement {
    sid    = "DynamoDBAccess"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchWriteItem",
      "dynamodb:BatchGetItem",
    ]
    resources = [
      aws_dynamodb_table.jobs.arn,
      "${aws_dynamodb_table.jobs.arn}/index/*",
      aws_dynamodb_table.users.arn,
    ]
  }
}

resource "aws_iam_role_policy" "ecs_task_dynamodb" {
  name   = "${var.project_name}-ecs-dynamodb-policy"
  role   = aws_iam_role.ecs_task.id
  policy = data.aws_iam_policy_document.dynamodb_access.json
}

# ── Política: SQS Access ─────────────────────────────────────

data "aws_iam_policy_document" "sqs_access" {
  statement {
    sid    = "SQSAccess"
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ChangeMessageVisibility",
    ]
    resources = [
      aws_sqs_queue.jobs.arn,
      aws_sqs_queue.jobs_dlq.arn,
    ]
  }
}

resource "aws_iam_role_policy" "ecs_task_sqs" {
  name   = "${var.project_name}-ecs-sqs-policy"
  role   = aws_iam_role.ecs_task.id
  policy = data.aws_iam_policy_document.sqs_access.json
}
