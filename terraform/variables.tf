variable "image" {
  default = "CentOS7-Cloud"
}

variable "flavor" {
  default = "s1.capacious"
}

variable "flavor_monitor" {
  default = "s1.small"
}

variable "ssh_key_file" {
  default = "sequence_search_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "e25c3173-bb5c-4bbc-83a7-f0551099c8cd"  # ext-net-36
}

variable "default_floating_ip" {
  default = "193.62.55.40"
}

variable "test_floating_ip" {
  default = "193.62.55.123"
}

variable "covid_floating_ip" {
  default = "193.62.55.100"
}

variable "default_instances" {
  default = 30
}

variable "test_instances" {
  default = 7
}

variable "covid_instances" {
  default = 2
}

variable "default_tfstate" {
  default = "terraform.tfstate"
}

variable "test_tfstate" {
  default = "terraform.tfstate.d/test/terraform.tfstate"
}

variable "covid_tfstate" {
  default = "terraform.tfstate.d/covid/terraform.tfstate"
}
