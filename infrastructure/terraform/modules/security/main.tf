terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Simplified Security Module - Fixed circular dependency
# For production, implement with separate security group resources and rules

# Application Security Group
resource "aws_security_group" "app" {
  name_prefix = "${var.app_name}-${var.environment}-app-"
  description = "Security group for application tier"
  vpc_id      = var.vpc_id

  # Allow HTTPS inbound
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS inbound"
  }

  # Allow HTTP inbound (for redirect)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTP inbound"
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-app-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Database Security Group
resource "aws_security_group" "database" {
  name_prefix = "${var.app_name}-${var.environment}-db-"
  description = "Security group for database tier"
  vpc_id      = var.vpc_id

  # Allow MySQL from app security group
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "MySQL from application"
  }

  # Allow outbound for updates
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound"
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-db-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Cache Security Group (Redis)
resource "aws_security_group" "cache" {
  name_prefix = "${var.app_name}-${var.environment}-cache-"
  description = "Security group for cache tier (Redis)"
  vpc_id      = var.vpc_id

  # Allow Redis from app security group
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Redis from application"
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-cache-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Admin Access Security Group
resource "aws_security_group" "admin" {
  name_prefix = "${var.app_name}-${var.environment}-admin-"
  description = "Security group for administrative access"
  vpc_id      = var.vpc_id

  # SSH from admin CIDR blocks
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.admin_cidr_blocks
    description = "SSH from admin networks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-${var.environment}-admin-sg"
  })
}
