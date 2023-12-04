variable "image" {
  default = "CentOS-Stream-GenericCloud-8-20220125"
}

variable "flavor" {
  default = "4c8m80d"  # 4 vcpu | 8GB RAM | 80GB disk
}

variable "flavor_nfs_server" {
  default = "2c2m80d"  # 2 vcpu | 2GB RAM | 80GB disk
}

variable "flavor_monitor" {
  default = "1c2m20d"  # 1 vcpu | 2GB RAM | 20GB disk
}

variable "ssh_key_file" {
  default = "sequence_search_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "9948edde-640b-482b-a6bc-ad1466000d86"
}

variable "default_floating_ip" {
  default = "45.88.81.147"
}

variable "test_floating_ip" {
  default = "45.88.80.122"
}

variable "litscan_prefer_floating_ip" {
  default = "45.88.81.188"
}

variable "default_instances" {
  default = 30
}

variable "test_instances" {
  default = 10
}

variable "one_hundred" {
  default = 100
}

variable "two_hundred" {
  default = 200
}

variable "default_tfstate" {
  default = "terraform.tfstate"
}

variable "test_tfstate" {
  default = "terraform.tfstate.d/test/terraform.tfstate"
}
