variable "image" {
  default = "centos-stream-8-v20220128"
}

variable "flavor" {
  default = "e2-standard-2"  # 2 vcpu | 8GB RAM | 50GB disk
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
  default = 1
}

variable "default_tfstate" {
  default = "terraform.tfstate"
}
