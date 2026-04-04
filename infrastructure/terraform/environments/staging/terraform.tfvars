aws_region  = "us-west-2"
environment = "staging"
app_name    = "fluxora"

vpc_cidr             = "10.1.0.0/16"
availability_zones   = ["us-west-2a", "us-west-2b", "us-west-2c"]
public_subnet_cidrs  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
private_subnet_cidrs = ["10.1.4.0/24", "10.1.5.0/24", "10.1.6.0/24"]

instance_type = "t3.medium"
key_name      = "staging-key"

db_instance_class = "db.t3.medium"
db_name           = "fluxoradb"
db_username       = "admin"
db_password       = "CHANGE_ME_USE_SECRETS_MANAGER"

default_tags = {
  Terraform   = "true"
  Environment = "staging"
  Project     = "fluxora"
  ManagedBy   = "terraform"
}

admin_cidr_blocks = ["10.0.0.0/8"]
