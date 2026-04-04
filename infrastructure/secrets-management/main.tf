# Secrets Management Infrastructure for Financial Standards Compliance
# This module provides secure secrets management using AWS Secrets Manager and Parameter Store

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# KMS Key for Secrets Encryption (separate from main security KMS key)
resource "aws_kms_key" "secrets" {
  description             = "KMS key for secrets encryption - ${var.app_name}-${var.environment}"
  deletion_window_in_days = var.kms_deletion_window
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:CreateGrant"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow Systems Manager Parameter Store"
        Effect = "Allow"
        Principal = {
          Service = "ssm.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-secrets-kms"
    Type = "secrets-encryption"
  })
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.app_name}-${var.environment}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# Database Credentials
resource "random_password" "db_master_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "db_master_credentials" {
  name                    = "${var.app_name}/${var.environment}/database/master"
  description             = "Master database credentials for ${var.app_name} ${var.environment}"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  dynamic "replica" {
    for_each = var.replica_region != "" && var.replica_region != data.aws_region.current.name ? [1] : []
    content {
      region = var.replica_region
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-db-master-secret"
    Type = "database-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "db_master_credentials" {
  secret_id = aws_secretsmanager_secret.db_master_credentials.id
  secret_string = jsonencode({
    username = var.db_master_username
    password = random_password.db_master_password.result
    engine   = "mysql"
    host     = var.db_host
    port     = var.db_port
    dbname   = var.db_name
  })
}

# Application Database User Credentials
resource "random_password" "db_app_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "db_app_credentials" {
  name                    = "${var.app_name}/${var.environment}/database/application"
  description             = "Application database credentials for ${var.app_name} ${var.environment}"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  dynamic "replica" {
    for_each = var.replica_region != "" && var.replica_region != data.aws_region.current.name ? [1] : []
    content {
      region = var.replica_region
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-db-app-secret"
    Type = "database-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "db_app_credentials" {
  secret_id = aws_secretsmanager_secret.db_app_credentials.id
  secret_string = jsonencode({
    username = var.db_app_username
    password = random_password.db_app_password.result
    engine   = "mysql"
    host     = var.db_host
    port     = var.db_port
    dbname   = var.db_name
  })
}

# Redis/Cache Credentials
resource "random_password" "redis_auth_token" {
  length  = 64
  special = false  # Redis auth tokens should not contain special characters
}

resource "aws_secretsmanager_secret" "redis_credentials" {
  name                    = "${var.app_name}/${var.environment}/cache/redis"
  description             = "Redis cache credentials for ${var.app_name} ${var.environment}"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  dynamic "replica" {
    for_each = var.replica_region != "" && var.replica_region != data.aws_region.current.name ? [1] : []
    content {
      region = var.replica_region
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-redis-secret"
    Type = "cache-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "redis_credentials" {
  secret_id = aws_secretsmanager_secret.redis_credentials.id
  secret_string = jsonencode({
    auth_token = random_password.redis_auth_token.result
    host       = var.redis_host
    port       = var.redis_port
  })
}

# Application Secrets
resource "random_password" "app_secret_key" {
  length  = 64
  special = true
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.app_name}/${var.environment}/application/secrets"
  description             = "Application secrets for ${var.app_name} ${var.environment}"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  dynamic "replica" {
    for_each = var.replica_region != "" && var.replica_region != data.aws_region.current.name ? [1] : []
    content {
      region = var.replica_region
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-app-secrets"
    Type = "application-secrets"
  })
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    secret_key    = random_password.app_secret_key.result
    jwt_secret    = random_password.jwt_secret.result
    encryption_key = base64encode(random_password.app_secret_key.result)
  })
}

# API Keys and External Service Credentials
resource "aws_secretsmanager_secret" "external_apis" {
  name                    = "${var.app_name}/${var.environment}/external/apis"
  description             = "External API credentials for ${var.app_name} ${var.environment}"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  dynamic "replica" {
    for_each = var.replica_region != "" && var.replica_region != data.aws_region.current.name ? [1] : []
    content {
      region = var.replica_region
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-external-apis"
    Type = "external-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "external_apis" {
  secret_id = aws_secretsmanager_secret.external_apis.id
  secret_string = jsonencode(var.external_api_credentials)
}

# SSL/TLS Certificates
resource "aws_secretsmanager_secret" "ssl_certificates" {
  name                    = "${var.app_name}/${var.environment}/ssl/certificates"
  description             = "SSL/TLS certificates for ${var.app_name} ${var.environment}"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  dynamic "replica" {
    for_each = var.replica_region != "" && var.replica_region != data.aws_region.current.name ? [1] : []
    content {
      region = var.replica_region
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-ssl-certs"
    Type = "ssl-certificates"
  })
}

# Systems Manager Parameter Store for non-sensitive configuration
resource "aws_ssm_parameter" "app_config" {
  for_each = var.app_configuration

  name  = "/${var.app_name}/${var.environment}/config/${each.key}"
  type  = each.value.sensitive ? "SecureString" : "String"
  value = each.value.value
  key_id = each.value.sensitive ? aws_kms_key.secrets.arn : null

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-config-${each.key}"
    Type = "configuration"
  })
}

# IAM Role for Secrets Access
resource "aws_iam_role" "secrets_access_role" {
  name = "${var.app_name}-${var.environment}-secrets-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ec2.amazonaws.com",
            "ecs-tasks.amazonaws.com",
            "lambda.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-secrets-role"
    Type = "iam-role"
  })
}

resource "aws_iam_role_policy" "secrets_access_policy" {
  name = "${var.app_name}-${var.environment}-secrets-access-policy"
  role = aws_iam_role.secrets_access_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.db_master_credentials.arn,
          aws_secretsmanager_secret.db_app_credentials.arn,
          aws_secretsmanager_secret.redis_credentials.arn,
          aws_secretsmanager_secret.app_secrets.arn,
          aws_secretsmanager_secret.external_apis.arn,
          aws_secretsmanager_secret.ssl_certificates.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.app_name}/${var.environment}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.secrets.arn
      }
    ]
  })
}

resource "aws_iam_instance_profile" "secrets_access_profile" {
  name = "${var.app_name}-${var.environment}-secrets-access-profile"
  role = aws_iam_role.secrets_access_role.name

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-secrets-profile"
    Type = "iam-profile"
  })
}

# Secrets Rotation Lambda Function
resource "aws_iam_role" "secrets_rotation_role" {
  name = "${var.app_name}-${var.environment}-secrets-rotation"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-rotation-role"
    Type = "iam-role"
  })
}

resource "aws_iam_role_policy" "secrets_rotation_policy" {
  name = "${var.app_name}-${var.environment}-secrets-rotation-policy"
  role = aws_iam_role.secrets_rotation_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage"
        ]
        Resource = [
          aws_secretsmanager_secret.db_master_credentials.arn,
          aws_secretsmanager_secret.db_app_credentials.arn,
          aws_secretsmanager_secret.redis_credentials.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.secrets.arn
      }
    ]
  })
}

# CloudWatch Log Group for Secrets Access Monitoring
resource "aws_cloudwatch_log_group" "secrets_access_logs" {
  name              = "/aws/secretsmanager/${var.app_name}/${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.secrets.arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-secrets-logs"
    Type = "monitoring"
  })
}

# CloudWatch Alarms for Secrets Access
resource "aws_cloudwatch_metric_alarm" "secrets_access_failures" {
  alarm_name          = "${var.app_name}-${var.environment}-secrets-access-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "GetSecretValueErrors"
  namespace           = "AWS/SecretsManager"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors secrets access failures"
  alarm_actions       = var.alarm_notification_arns

  dimensions = {
    SecretArn = aws_secretsmanager_secret.db_master_credentials.arn
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-secrets-alarm"
    Type = "monitoring"
  })
}

# Backup and Recovery for Secrets
resource "aws_backup_vault" "secrets_backup" {
  name        = "${var.app_name}-${var.environment}-secrets-backup"
  kms_key_arn = aws_kms_key.secrets.arn

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-secrets-backup-vault"
    Type = "backup"
  })
}
