# Compliance Infrastructure for Financial Standards
# This module implements compliance monitoring and reporting for PCI DSS, GDPR, SOC 2, and other financial standards

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# AWS Config Rules for PCI DSS Compliance
resource "aws_config_config_rule" "pci_dss_rules" {
  for_each = var.pci_dss_rules

  name = "${var.app_name}-${var.environment}-${each.key}"

  source {
    owner             = "AWS"
    source_identifier = each.value.source_identifier
  }

  input_parameters = jsonencode(each.value.input_parameters)

  # Note: ensure AWS Config recorder is active before applying

  tags = merge(var.common_tags, {
    Name       = "${var.app_name}-${var.environment}-${each.key}"
    Compliance = "pci-dss"
    Standard   = each.value.standard
  })
}

# AWS Config Rules for GDPR Compliance
resource "aws_config_config_rule" "gdpr_rules" {
  for_each = var.gdpr_rules

  name = "${var.app_name}-${var.environment}-${each.key}"

  source {
    owner             = "AWS"
    source_identifier = each.value.source_identifier
  }

  input_parameters = jsonencode(each.value.input_parameters)

  # Note: ensure AWS Config recorder is active before applying

  tags = merge(var.common_tags, {
    Name       = "${var.app_name}-${var.environment}-${each.key}"
    Compliance = "gdpr"
    Standard   = each.value.standard
  })
}

# AWS Config Rules for SOC 2 Compliance
resource "aws_config_config_rule" "soc2_rules" {
  for_each = var.soc2_rules

  name = "${var.app_name}-${var.environment}-${each.key}"

  source {
    owner             = "AWS"
    source_identifier = each.value.source_identifier
  }

  input_parameters = jsonencode(each.value.input_parameters)

  # Note: ensure AWS Config recorder is active before applying

  tags = merge(var.common_tags, {
    Name       = "${var.app_name}-${var.environment}-${each.key}"
    Compliance = "soc2"
    Standard   = each.value.standard
  })
}

# Custom Config Rule for Financial Data Classification
resource "aws_config_config_rule" "data_classification" {
  name = "${var.app_name}-${var.environment}-data-classification"

  source {
    owner                = "AWS"
    source_identifier    = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }

  # Note: ensure AWS Config recorder is active before applying

  tags = merge(var.common_tags, {
    Name       = "${var.app_name}-${var.environment}-data-classification"
    Compliance = "financial-data-protection"
  })
}

# Compliance Dashboard using CloudWatch
resource "aws_cloudwatch_dashboard" "compliance_dashboard" {
  dashboard_name = "${var.app_name}-${var.environment}-compliance"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Config", "ComplianceByConfigRule", "ConfigRuleName", "${var.app_name}-${var.environment}-encryption-enabled"],
            [".", ".", ".", "${var.app_name}-${var.environment}-access-logging-enabled"],
            [".", ".", ".", "${var.app_name}-${var.environment}-mfa-enabled"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Compliance Status Overview"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '/aws/config/compliance' | fields @timestamp, configRuleName, complianceType, resourceId\n| filter complianceType = \"NON_COMPLIANT\"\n| sort @timestamp desc\n| limit 100"
          region  = data.aws_region.current.name
          title   = "Non-Compliant Resources"
          view    = "table"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-dashboard"
    Type = "monitoring"
  })
}

# SNS Topic for Compliance Notifications
resource "aws_sns_topic" "compliance_notifications" {
  name              = "${var.app_name}-${var.environment}-compliance-alerts"
  kms_master_key_id = var.kms_key_id

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-sns"
    Type = "notifications"
  })
}

resource "aws_sns_topic_policy" "compliance_notifications" {
  arn = aws_sns_topic.compliance_notifications.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.compliance_notifications.arn
      }
    ]
  })
}

# EventBridge Rules for Compliance Events
resource "aws_cloudwatch_event_rule" "compliance_violations" {
  name        = "${var.app_name}-${var.environment}-compliance-violations"
  description = "Capture compliance violations"

  event_pattern = jsonencode({
    source      = ["aws.config"]
    detail-type = ["Config Rules Compliance Change"]
    detail = {
      newEvaluationResult = {
        complianceType = ["NON_COMPLIANT"]
      }
    }
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-events"
    Type = "monitoring"
  })
}

resource "aws_cloudwatch_event_target" "compliance_violations_target" {
  rule      = aws_cloudwatch_event_rule.compliance_violations.name
  target_id = "ComplianceViolationTarget"
  arn       = aws_sns_topic.compliance_notifications.arn
}

# Lambda Function for Compliance Reporting
resource "aws_iam_role" "compliance_lambda_role" {
  name = "${var.app_name}-${var.environment}-compliance-lambda-role"

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
    Name = "${var.app_name}-${var.environment}-compliance-lambda-role"
    Type = "iam"
  })
}

resource "aws_iam_role_policy" "compliance_lambda_policy" {
  name = "${var.app_name}-${var.environment}-compliance-lambda-policy"
  role = aws_iam_role.compliance_lambda_role.id

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
          "config:GetComplianceDetailsByConfigRule",
          "config:GetComplianceSummaryByConfigRule",
          "config:DescribeConfigRules",
          "config:GetResourceConfigHistory"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${var.compliance_reports_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# S3 Bucket for Compliance Reports
resource "aws_s3_bucket" "compliance_reports" {
  bucket        = "${var.app_name}-${var.environment}-compliance-reports-${random_id.bucket_suffix.hex}"
  force_destroy = var.environment != "prod"

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-reports"
    Type = "compliance-storage"
  })
}

resource "aws_s3_bucket_versioning" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.kms_key_id
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id

  rule {
    id     = "compliance_reports_lifecycle"
    status = "Enabled"

    expiration {
      days = var.compliance_report_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Lambda Function for Automated Compliance Reporting
data "archive_file" "compliance_lambda_zip" {
  type        = "zip"
  output_path = "/tmp/compliance_lambda.zip"
  source {
    content  = file("${path.module}/lambda/compliance_reporter.py")
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "compliance_reporter" {
  filename         = data.archive_file.compliance_lambda_zip.output_path
  function_name    = "${var.app_name}-${var.environment}-compliance-reporter"
  role            = aws_iam_role.compliance_lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.compliance_lambda_zip.output_base64sha256
  runtime         = "python3.12"
  timeout         = 300

  environment {
    variables = {
      APP_NAME    = var.app_name
      ENVIRONMENT = var.environment
      BUCKET_NAME = aws_s3_bucket.compliance_reports.bucket
      SNS_TOPIC   = aws_sns_topic.compliance_notifications.arn
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-lambda"
    Type = "compliance-automation"
  })
}

# CloudWatch Event Rule for Scheduled Compliance Reports
resource "aws_cloudwatch_event_rule" "compliance_report_schedule" {
  name                = "${var.app_name}-${var.environment}-compliance-report-schedule"
  description         = "Trigger compliance report generation"
  schedule_expression = var.compliance_report_schedule

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-schedule"
    Type = "automation"
  })
}

resource "aws_cloudwatch_event_target" "compliance_report_target" {
  rule      = aws_cloudwatch_event_rule.compliance_report_schedule.name
  target_id = "ComplianceReportTarget"
  arn       = aws_lambda_function.compliance_reporter.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.compliance_reporter.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.compliance_report_schedule.arn
}

# Data Loss Prevention (DLP) Configuration
resource "aws_macie2_account" "main" {
  finding_publishing_frequency = "FIFTEEN_MINUTES"
  status                      = "ENABLED"

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-macie"
    Type = "data-protection"
  })
}

# Custom Classification Job for Financial Data
resource "aws_macie2_classification_job" "financial_data" {
  job_type = "ONE_TIME"
  name     = "${var.app_name}-${var.environment}-financial-data-classification"

  s3_job_definition {
    bucket_definitions {
      account_id = data.aws_caller_identity.current.account_id
      buckets    = [var.app_data_bucket_name]
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-financial-classification"
    Type = "data-classification"
  })
}

# AWS Systems Manager Compliance
resource "aws_ssm_association" "compliance_baseline" {
  name = "AWS-GatherSoftwareInventory"

  targets {
    key    = "InstanceIds"
    values = ["*"]
  }

  schedule_expression = "rate(1 day)"

  parameters = {
    applications         = "Enabled"
    awsComponents       = "Enabled"
    customInventory     = "Enabled"
    instanceDetailedInformation = "Enabled"
    networkConfig       = "Enabled"
    services            = "Enabled"
    windowsRegistry     = "Enabled"
    windowsRoles        = "Enabled"
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-compliance-inventory"
    Type = "compliance-automation"
  })
}

# Patch Compliance
resource "aws_ssm_patch_baseline" "compliance_baseline" {
  name             = "${var.app_name}-${var.environment}-patch-baseline"
  description      = "Patch baseline for compliance requirements"
  operating_system = "AMAZON_LINUX_2"

  approval_rule {
    approve_after_days  = 0
    enable_non_security = true

    patch_filter {
      key    = "CLASSIFICATION"
      values = ["Security", "Bugfix", "Critical"]
    }

    patch_filter {
      key    = "SEVERITY"
      values = ["Critical", "Important"]
    }
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-patch-baseline"
    Type = "compliance-patching"
  })
}

# Compliance Remediation Automation
resource "aws_config_remediation_configuration" "auto_remediation" {
  for_each = var.auto_remediation_rules

  config_rule_name = aws_config_config_rule.pci_dss_rules[each.key].name

  resource_type    = each.value.resource_type
  target_type      = "SSM_DOCUMENT"
  target_id        = each.value.ssm_document
  target_version   = "1"
  automatic        = each.value.automatic
  maximum_automatic_attempts = each.value.max_attempts

  parameter {
    name           = "AutomationAssumeRole"
    static_value   = aws_iam_role.remediation_role.arn
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-auto-remediation-${each.key}"
    Type = "compliance-remediation"
  })
}

# IAM Role for Remediation
resource "aws_iam_role" "remediation_role" {
  name = "${var.app_name}-${var.environment}-remediation-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ssm.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-remediation-role"
    Type = "iam"
  })
}

resource "aws_iam_role_policy" "remediation_policy" {
  name = "${var.app_name}-${var.environment}-remediation-policy"
  role = aws_iam_role.remediation_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "s3:*",
          "rds:*",
          "kms:*",
          "iam:*",
          "logs:*"
        ]
        Resource = "*"
      }
    ]
  })
}
