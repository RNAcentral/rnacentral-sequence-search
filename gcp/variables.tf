variable "image" {
  default = "centos-stream-8-v20220128"
}

variable "flavor" {
  default = "e2-standard-2"  # 2 vcpu | 8GB RAM | 50GB disk
}

variable "flavor-medium" {
  default = "e2-medium"  # 2 vcpu | 4GB RAM | 20GB disk
}

variable "flavor-small" {
  default = "e2-small"  # 2 vcpu | 2GB RAM | 10GB disk
}

variable "region" {
  default = "europe-west2-a"
}

variable "ssh_key_file" {
  default = "gcp_rsa.pub"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "default_instances" {
  default = 8
}

variable "test_instances" {
  default = 4
}

variable "default_tfstate" {
  default = "terraform.tfstate"
}

variable "test_tfstate" {
  default = "terraform.tfstate.d/test/terraform.tfstate"
}
