variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "force_destroy" {
  description = "Allow force destroy of S3 buckets"
  type        = bool
  default     = false
}
