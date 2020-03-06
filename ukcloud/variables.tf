variable "image" {
  default = "Centos-7-Latest"
}

variable "flavor" {
  default = "m1.small"
}

variable "flavor_monitor" {
  default = "t1.small"
}

variable "ssh_key_file" {
  default = "sequence_search_rsa"
}

variable "ssh_user_name" {
  default = "centos"
}

variable "external_network_id" {
  default = "83f24d94-edea-4c40-b4c0-6f9ede5c9305"  # internet
}

variable "default_floating_ip" {
  default = "51.179.208.80"
}

variable "test_floating_ip" {
  default = "51.179.208.74"
}

variable "default_instances" {
  default = 15
}

variable "test_instances" {
  default = 2
}

variable "default_tfstate" {
  default = "terraform.tfstate"
}

variable "test_tfstate" {
  default = "terraform.tfstate.d/test/terraform.tfstate"
}
