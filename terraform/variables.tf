variable "image" {
  default = "CentOS-8-GenericCloud-8.1"
}

variable "flavor" {
  default = "4c6m50d"
}

variable "flavor_monitor" {
  default = "1c2m20d"
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

variable "covid_floating_ip" {
  default = "45.88.81.141"
}

variable "default_instances" {
  default = 40
}

variable "test_instances" {
  default = 10
}

variable "covid_instances" {
  default = 2
}

variable "fifty" {
  default = 50
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

variable "covid_tfstate" {
  default = "terraform.tfstate.d/covid/terraform.tfstate"
}
