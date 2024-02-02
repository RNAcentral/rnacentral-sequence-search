variable "image" {
  default = "CentOS-Stream-GenericCloud-9"
}

variable "flavor" {
  default = "4c8m80d"  # 4 vcpu | 8GB RAM | 80GB disk
}

variable "flavor_6gb_ram" {
  default = "4c6m50d"  # 4 vcpu | 6GB RAM | 50GB disk
}

variable "ssh_key_file" {
  default = "sequence_search_rsa"
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
