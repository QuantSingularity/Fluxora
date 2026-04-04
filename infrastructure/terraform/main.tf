terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    # Will be configured per environment
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.default_tags
  }
}

module "network" {
  source = "./modules/network"

  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "security" {
  source = "./modules/security"

  environment         = var.environment
  vpc_id              = module.network.vpc_id
  vpc_cidr            = var.vpc_cidr
  app_name            = var.app_name
  admin_cidr_blocks   = var.admin_cidr_blocks
}

module "compute" {
  source = "./modules/compute"

  environment        = var.environment
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  public_subnet_ids  = module.network.public_subnet_ids
  instance_type      = var.instance_type
  key_name           = var.key_name
  app_name           = var.app_name
  security_group_ids = [module.security.app_security_group_id]
  certificate_arn    = var.certificate_arn
}

module "database" {
  source = "./modules/database"

  environment        = var.environment
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  db_instance_class  = var.db_instance_class
  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = var.db_password
  security_group_ids = [module.security.db_security_group_id]
}

module "storage" {
  source = "./modules/storage"

  environment = var.environment
  app_name    = var.app_name
}
