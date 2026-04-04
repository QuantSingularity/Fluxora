# Secrets Management Module Variables

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "common_tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default = {
    Project     = "fluxora"
    ManagedBy   = "terraform"
    Compliance  = "pci-dss,gdpr,soc2"
  }
}

variable "kms_deletion_window" {
  description = "Number of days before KMS key deletion (7-30)"
  type        = number
  default     = 30
  validation {
    condition     = var.kms_deletion_window >= 7 && var.kms_deletion_window <= 30
    error_message = "KMS deletion window must be between 7 and 30 days."
  }
}

variable "replica_region" {
  description = "AWS region for secrets replication"
  type        = string
  default     = ""
}

# Database Configuration
variable "db_master_username" {
  description = "Master username for database"
  type        = string
  default     = "admin"
}

variable "db_app_username" {
  description = "Application username for database"
  type        = string
  default     = "fluxora_app"
}

variable "db_host" {
  description = "Database host endpoint"
  type        = string
  default     = ""
}

variable "db_port" {
  description = "Database port"
  type        = number
  default     = 3306
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "fluxora"
}

# Redis Configuration
variable "redis_host" {
  description = "Redis host endpoint"
  type        = string
  default     = ""
}

variable "redis_port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

# External API Credentials
variable "external_api_credentials" {
  description = "External API credentials and keys"
  type        = map(string)
  default     = {}
  sensitive   = true
}

# Application Configuration
variable "app_configuration" {
  description = "Application configuration parameters"
  type = map(object({
    value     = string
    sensitive = bool
  }))
  default = {
    debug_mode = {
      value     = "false"
      sensitive = false
    }
    log_level = {
      value     = "INFO"
      sensitive = false
    }
    session_timeout = {
      value     = "3600"
      sensitive = false
    }
    max_connections = {
      value     = "100"
      sensitive = false
    }
  }
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 90
  validation {
    condition     = var.log_retention_days >= 30
    error_message = "Log retention must be at least 30 days for compliance."
  }
}

variable "alarm_notification_arns" {
  description = "List of SNS topic ARNs for alarm notifications"
  type        = list(string)
  default     = []
}

variable "enable_secrets_rotation" {
  description = "Enable automatic secrets rotation"
  type        = bool
  default     = true
}

variable "rotation_schedule_days" {
  description = "Number of days between automatic secret rotations"
  type        = number
  default     = 30
  validation {
    condition     = var.rotation_schedule_days >= 1 && var.rotation_schedule_days <= 365
    error_message = "Rotation schedule must be between 1 and 365 days."
  }
}

variable "backup_retention_days" {
  description = "Number of days to retain secret backups"
  type        = number
  default     = 90
  validation {
    condition     = var.backup_retention_days >= 30
    error_message = "Backup retention must be at least 30 days for compliance."
  }
}

variable "cross_region_backup_enabled" {
  description = "Enable cross-region backup for secrets"
  type        = bool
  default     = true
}

variable "secrets_access_logging_enabled" {
  description = "Enable detailed logging for secrets access"
  type        = bool
  default     = true
}

variable "compliance_requirements" {
  description = "Compliance requirements for secrets management"
  type        = object({
    pci_dss_required = bool
    gdpr_required    = bool
    soc2_required    = bool
    hipaa_required   = bool
  })
  default = {
    pci_dss_required = true
    gdpr_required    = true
    soc2_required    = true
    hipaa_required   = false
  }
}

variable "allowed_principals" {
  description = "List of IAM principals allowed to access secrets"
  type        = list(string)
  default     = []
}

variable "denied_principals" {
  description = "List of IAM principals explicitly denied access to secrets"
  type        = list(string)
  default     = []
}

variable "ip_restrictions" {
  description = "IP address restrictions for secrets access"
  type        = object({
    enabled        = bool
    allowed_cidrs  = list(string)
    denied_cidrs   = list(string)
  })
  default = {
    enabled       = false
    allowed_cidrs = []
    denied_cidrs  = []
  }
}

variable "time_based_access" {
  description = "Time-based access restrictions"
  type        = object({
    enabled    = bool
    start_time = string  # HH:MM format
    end_time   = string  # HH:MM format
    timezone   = string
  })
  default = {
    enabled    = false
    start_time = "09:00"
    end_time   = "17:00"
    timezone   = "UTC"
  }
}

variable "secret_sharing_enabled" {
  description = "Enable cross-account secret sharing"
  type        = bool
  default     = false
}

variable "shared_accounts" {
  description = "List of AWS account IDs for secret sharing"
  type        = list(string)
  default     = []
}

variable "audit_trail_enabled" {
  description = "Enable comprehensive audit trail for secrets"
  type        = bool
  default     = true
}

variable "data_residency_requirements" {
  description = "Data residency requirements for secrets"
  type        = object({
    primary_region   = string
    allowed_regions  = list(string)
    forbidden_regions = list(string)
  })
  default = {
    primary_region    = "us-east-1"
    allowed_regions   = ["us-east-1", "us-west-2"]
    forbidden_regions = []
  }
}
