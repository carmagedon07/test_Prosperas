terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Estado local — suficiente para el challenge.
  # Para producción real usar S3 backend + DynamoDB lock.
}

provider "aws" {
  region = var.aws_region
}

# ── Red: VPC default de AWS (ya existe en cada cuenta) ────────────────
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ── Identidad de la cuenta (para nombres únicos de recursos) ──────────
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
